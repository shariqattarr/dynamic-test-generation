import re
from pathlib import Path
from src.loader import SmokeConfig, TestCase


def _sanitize_name(name: str) -> str:
    """Convert test name to valid python function name"""
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "test"


def _generate_test_func(test: TestCase, base_url: str) -> str:
    """Generate a single test function"""
    func_name = f"test_{_sanitize_name(test.name)}"
    url = f"{base_url}{test.path}"
    
    lines = []
    lines.append(f"def {func_name}():")
    lines.append(f'    """Test: {test.name}"""')
    
    # build request kwargs
    req_kwargs = []
    if test.headers:
        lines.append(f"    headers = {repr(test.headers)}")
        req_kwargs.append("headers=headers")
    if test.body:
        lines.append(f"    payload = {repr(test.body)}")
        req_kwargs.append("json=payload")
    
    kwargs_str = ", ".join(req_kwargs)
    if kwargs_str:
        kwargs_str = ", " + kwargs_str
    
    lines.append(f'    response = httpx.{test.method.lower()}("{url}"{kwargs_str})')
    lines.append("")
    lines.append(f"    assert response.status_code == {test.expect_status}, \\")
    lines.append(f'        f"Expected status {test.expect_status}, got {{response.status_code}}"')
    
    if test.expect_body:
        lines.append("")
        lines.append(f"    expected_body = {repr(test.expect_body)}")
        lines.append("    assert_diff(expected_body, response.json())")
    
    if test.expect_body_schema:
        lines.append("")
        lines.append(f"    schema = {repr(test.expect_body_schema)}")
        lines.append('    assert_schema(response.json(), schema)')
    
    return "\n".join(lines)


def generate_tests(config: SmokeConfig, output_path: str | Path) -> Path:
    """Generate test_smoke.py from config"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = [
        '"""Auto-generated smoke tests"""',
        "import httpx",
        "from src.diff_engine import assert_diff, assert_schema",
        "",
        "",
    ]
    
    for test in config.tests:
        lines.append(_generate_test_func(test, config.base_url))
        lines.append("")
        lines.append("")
    
    content = "\n".join(lines).rstrip() + "\n"
    output_path.write_text(content)
    
    return output_path
