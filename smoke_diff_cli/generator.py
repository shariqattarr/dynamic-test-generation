import re
from pathlib import Path
from smoke_diff_cli.loader import SmokeConfig, TestCase


def _sanitize_name(name: str) -> str:
    """Convert test name to valid python function name"""
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "test"


def _generate_test_func(test: TestCase, base_url: str) -> str:
    """Generate a single test function with proper error handling"""
    func_name = f"test_{_sanitize_name(test.name)}"
    url = f"{base_url}{test.path}"
    
    lines = []
    lines.append(f"def {func_name}():")
    lines.append(f'    """Test: {test.name}"""')
    lines.append(f"    print(f'\\n  → Testing: {test.name}')")
    
    # request kwargs
    req_kwargs = [f"timeout={test.timeout}"]
    if test.headers:
        lines.append(f"    headers = {repr(test.headers)}")
        req_kwargs.append("headers=headers")
    if test.body:
        lines.append(f"    payload = {repr(test.body)}")
        req_kwargs.append("json=payload")
    
    kwargs_str = ", ".join(req_kwargs)
    
    lines.append(f"")
    lines.append(f"    try:")
    lines.append(f'        response = httpx.{test.method.lower()}("{url}", {kwargs_str})')
    lines.append(f"    except httpx.TimeoutException:")
    lines.append(f'        raise AssertionError(f"Request timed out after {test.timeout}s")')
    lines.append(f"    except httpx.RequestError as e:")
    lines.append(f'        raise AssertionError(f"Request failed: {{e}}")')
    
    # check status first, before trying to parse json
    lines.append(f"")
    lines.append(f"    # check status before parsing body")
    lines.append(f"    assert response.status_code == {test.expect_status}, \\")
    lines.append(f'        f"Expected status {test.expect_status}, got {{response.status_code}}. Body: {{response.text[:200]}}"')
    
    if test.expect_body or test.expect_body_schema:
        lines.append(f"")
        lines.append(f"    # parse json (safe now since status is verified)")
        lines.append(f"    try:")
        lines.append(f"        body = response.json()")
        lines.append(f"    except Exception as e:")
        lines.append(f'        raise AssertionError(f"Failed to parse JSON: {{e}}. Body: {{response.text[:200]}}")')
    
    if test.expect_body:
        lines.append(f"")
        lines.append(f"    expected_body = {repr(test.expect_body)}")
        lines.append("    assert_diff(expected_body, body)")
    
    if test.expect_body_schema:
        lines.append(f"")
        lines.append(f"    schema = {repr(test.expect_body_schema)}")
        lines.append('    assert_schema(body, schema)')
    
    lines.append(f"")
    lines.append(f"    print(f'    ✓ Passed')")
    
    return "\n".join(lines)


def generate_tests(config: SmokeConfig, output_path: str | Path, dry_run: bool = False) -> tuple[Path, str]:
    """
    Generate test_smoke.py from config.
    Returns (output_path, content).
    If dry_run is True, doesn't write the file.
    """
    output_path = Path(output_path)
    
    lines = [
        '"""Auto-generated smoke tests - do not edit manually"""',
        "import httpx",
        "from smoke_diff_cli.diff_engine import assert_diff, assert_schema",
        "",
        "",
    ]
    
    for test in config.tests:
        lines.append(_generate_test_func(test, config.base_url))
        lines.append("")
        lines.append("")
    
    content = "\n".join(lines).rstrip() + "\n"
    
    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
    
    return output_path, content
