import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class TestCase:
    name: str
    path: str
    method: str
    expect_status: int
    expect_body_schema: Optional[dict] = None
    expect_body: Optional[dict] = None
    headers: Optional[dict] = None
    body: Optional[dict] = None


@dataclass
class SmokeConfig:
    base_url: str
    tests: list[TestCase]


def load_config(path: str | Path) -> SmokeConfig:
    """Load and parse smoke.yml config file"""
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    
    if not raw:
        raise ValueError("Empty config file")
    
    if "base_url" not in raw:
        raise ValueError("Missing required field: base_url")
    
    if "tests" not in raw or not raw["tests"]:
        raise ValueError("Missing or empty 'tests' field")
    
    tests = []
    for i, t in enumerate(raw["tests"]):
        if "name" not in t:
            raise ValueError(f"Test #{i+1}: missing 'name'")
        if "path" not in t:
            raise ValueError(f"Test '{t.get('name', i+1)}': missing 'path'")
        if "method" not in t:
            raise ValueError(f"Test '{t['name']}': missing 'method'")
        
        method = t["method"].upper()
        if method not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Test '{t['name']}': invalid method '{method}'")
        
        tests.append(TestCase(
            name=t["name"],
            path=t["path"],
            method=method,
            expect_status=t.get("expect_status", 200),
            expect_body_schema=t.get("expect_body_schema"),
            expect_body=t.get("expect_body"),
            headers=t.get("headers"),
            body=t.get("body"),
        ))
    
    return SmokeConfig(
        base_url=raw["base_url"].rstrip("/"),
        tests=tests,
    )
