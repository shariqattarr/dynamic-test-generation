# smoke-diff-cli

Generate and run smoke tests for your APIs from a simple YAML config.

I built this because I wanted to quickly verify APIs are working without writing boilerplate test code every time.

## Installation

```bash
pip install -e .
```

## Quick Start

1. Initialize a config file:
```bash
smoke-diff init
```

2. Edit `smoke.yml` with your API endpoints:
```yaml
base_url: https://jsonplaceholder.typicode.com
timeout: 30

tests:
  - name: Get All Users
    path: /users
    method: GET
    expect_status: 200

  - name: Get Single User
    path: /users/1
    method: GET
    expect_status: 200
    expect_body_schema:
      id: "int"
      name: "str"
      email: "str"
```

3. Run the tests:
```bash
smoke-diff run
```

## Commands

### `smoke-diff init [--force]`
Create a new `smoke.yml` config file. Use `--force` to overwrite existing.

### `smoke-diff generate [--dry-run]`
Generate `tests/test_smoke.py` from the config. `--dry-run` shows what will be generated without writing files.

### `smoke-diff run`
Generate tests and run them with pytest.

## Config Format

```yaml
base_url: https://api.example.com    # Required
timeout: 30                           # Optional: default timeout in seconds

tests:                                # Required: at least one test
  - name: Create User                 # Required: test name
    path: /users                      # Required: endpoint path
    method: POST                      # Required: GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS
    expect_status: 201                # Optional: default 200
    headers:                          # Optional: request headers
      Authorization: Bearer xyz
    body:                             # Optional: request body (JSON)
      name: John Doe
      email: john@example.com
    timeout: 10                       # Optional: override default timeout
    expect_body:                      # Optional: exact JSON match
      id: 1
      name: John Doe
    expect_body_schema:               # Optional: validate types only
      id: "int"
      name: "str"
```

## Examples

### Test with custom headers
```yaml
  - name: Protected Endpoint
    path: /profile
    method: GET
    headers:
      Authorization: Bearer YOUR_TOKEN
    expect_status: 200
```

### Test response schema
```yaml
  - name: List Products
    path: /products
    method: GET
    expect_status: 200
    expect_body_schema:
      - id: "int"
        name: "str"
        price: "float"
```

### Test POST request
```yaml
  - name: Create Order
    path: /orders
    method: POST
    body:
      product_id: 123
      quantity: 2
    expect_status: 201
    expect_body_schema:
      id: "int"
      status: "str"
```

## Output

Tests use Rich for nice output:
- ✅ Green checkmarks for passing tests
- 🔴 Red tables showing exact differences when assertions fail
- 📊 Diff trees for nested JSON comparisons

Run with `--verbose` flag to see what's happening:
```bash
smoke-diff run --verbose
```

## Features

- **Simple YAML config** - No code to write for basic tests
- **Schema validation** - Check field types without exact matches
- **Diff visualization** - See exactly what changed when tests fail
- **Timeout handling** - Never hang on slow APIs
- **Verbose mode** - Debug what's going on under the hood
- **Dry run** - Preview generated tests before writing files

## Troubleshooting

**ModuleNotFoundError: No module named 'smoke_diff_cli'**
```bash
pip install -e .
```

**Tests fail to find imports**
The tool sets PYTHONPATH automatically. Make sure you're running `smoke-diff run` from the project root.

**Request timeout error**
Increase the timeout in your config:
```yaml
timeout: 60
```

## License

MIT
