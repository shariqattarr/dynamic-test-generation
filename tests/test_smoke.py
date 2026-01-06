"""Auto-generated smoke tests"""
import httpx
from src.diff_engine import assert_diff, assert_schema


def test_get_users():
    """Test: Get Users"""
    response = httpx.get("https://api.example.com/users")

    assert response.status_code == 200, \
        f"Expected status 200, got {response.status_code}"

    schema = {'id': 'int', 'name': 'str'}
    assert_schema(response.json(), schema)
