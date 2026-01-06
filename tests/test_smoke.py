"""Auto-generated smoke tests - do not edit manually"""
import httpx
from smoke_diff_cli.diff_engine import assert_diff, assert_schema


def test_get_all_users():
    """Test: Get All Users"""
    print(f'\n  → Testing: Get All Users')

    try:
        response = httpx.get("https://jsonplaceholder.typicode.com/users", timeout=30)
    except httpx.TimeoutException:
        raise AssertionError(f"Request timed out after 30s")
    except httpx.RequestError as e:
        raise AssertionError(f"Request failed: {e}")

    # check status before parsing body
    assert response.status_code == 200, \
        f"Expected status 200, got {response.status_code}. Body: {response.text[:200]}"

    print(f'    ✓ Passed')


def test_get_single_user():
    """Test: Get Single User"""
    print(f'\n  → Testing: Get Single User')

    try:
        response = httpx.get("https://jsonplaceholder.typicode.com/users/1", timeout=30)
    except httpx.TimeoutException:
        raise AssertionError(f"Request timed out after 30s")
    except httpx.RequestError as e:
        raise AssertionError(f"Request failed: {e}")

    # check status before parsing body
    assert response.status_code == 200, \
        f"Expected status 200, got {response.status_code}. Body: {response.text[:200]}"

    # parse json (safe now since status is verified)
    try:
        body = response.json()
    except Exception as e:
        raise AssertionError(f"Failed to parse JSON: {e}. Body: {response.text[:200]}")

    schema = {'id': 'int', 'name': 'str', 'email': 'str'}
    assert_schema(body, schema)

    print(f'    ✓ Passed')
