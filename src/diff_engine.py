from deepdiff import DeepDiff
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import box

console = Console()


def _type_name(val):
    """Get readable type name"""
    if val is None:
        return "null"
    return type(val).__name__


def _render_diff_tree(diff: dict) -> Tree:
    """Render DeepDiff result as a Rich Tree"""
    tree = Tree("[bold red]Diff Details[/bold red]")
    
    if "values_changed" in diff:
        changed = tree.add("[yellow]Values Changed[/yellow]")
        for path, change in diff["values_changed"].items():
            old = change.get("old_value", "N/A")
            new = change.get("new_value", "N/A")
            changed.add(f"{path}: [red]{repr(old)}[/red] → [green]{repr(new)}[/green]")
    
    if "type_changes" in diff:
        types = tree.add("[magenta]Type Changes[/magenta]")
        for path, change in diff["type_changes"].items():
            old_type = change.get("old_type", type(None)).__name__
            new_type = change.get("new_type", type(None)).__name__
            types.add(f"{path}: [red]{old_type}[/red] → [green]{new_type}[/green]")
    
    if "dictionary_item_added" in diff:
        added = tree.add("[green]Items Added[/green]")
        for item in diff["dictionary_item_added"]:
            added.add(f"[green]+ {item}[/green]")
    
    if "dictionary_item_removed" in diff:
        removed = tree.add("[red]Items Removed[/red]")
        for item in diff["dictionary_item_removed"]:
            removed.add(f"[red]- {item}[/red]")
    
    if "iterable_item_added" in diff:
        added = tree.add("[green]List Items Added[/green]")
        for path, val in diff["iterable_item_added"].items():
            added.add(f"[green]+ {path}: {repr(val)}[/green]")
    
    if "iterable_item_removed" in diff:
        removed = tree.add("[red]List Items Removed[/red]")
        for path, val in diff["iterable_item_removed"].items():
            removed.add(f"[red]- {path}: {repr(val)}[/red]")
    
    return tree


def _render_diff_table(expected, actual, diff: dict) -> Table:
    """Render side-by-side comparison table"""
    table = Table(
        title="Expected vs Actual",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Field", style="dim")
    table.add_column("Expected", style="green")
    table.add_column("Actual", style="red")
    table.add_column("Status")
    
    all_keys = set()
    if isinstance(expected, dict):
        all_keys.update(expected.keys())
    if isinstance(actual, dict):
        all_keys.update(actual.keys())
    
    for key in sorted(all_keys):
        exp_val = expected.get(key, "[missing]") if isinstance(expected, dict) else "N/A"
        act_val = actual.get(key, "[missing]") if isinstance(actual, dict) else "N/A"
        
        if key not in (expected if isinstance(expected, dict) else {}):
            status = "[green]+ added[/green]"
        elif key not in (actual if isinstance(actual, dict) else {}):
            status = "[red]- removed[/red]"
        elif exp_val != act_val:
            status = "[yellow]~ changed[/yellow]"
        else:
            status = "[dim]✓[/dim]"
        
        table.add_row(str(key), repr(exp_val), repr(act_val), status)
    
    return table


def assert_diff(expected, actual, msg=""):
    """
    Compare expected and actual JSON values.
    If they differ, prints a Rich diff visualization and raises AssertionError.
    """
    diff = DeepDiff(expected, actual, ignore_order=True)
    
    if not diff:
        return True
    
    console.print()
    console.rule("[bold red]ASSERTION FAILED[/bold red]", style="red")
    
    if msg:
        console.print(f"[bold]{msg}[/bold]")
    console.print()
    
    if isinstance(expected, dict) and isinstance(actual, dict):
        table = _render_diff_table(expected, actual, diff)
        console.print(table)
        console.print()
    
    tree = _render_diff_tree(diff)
    console.print(tree)
    console.print()
    console.rule(style="red")
    
    raise AssertionError(f"JSON mismatch: {len(diff)} difference(s) found")


def check_schema(actual, schema: dict, path="root"):
    """
    Validate actual data against expected schema types.
    schema format: {"field": "int", "name": "str"}
    """
    type_map = {
        "int": int,
        "str": str,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "null": type(None),
    }
    
    errors = []
    
    if not isinstance(actual, dict):
        errors.append(f"{path}: expected dict, got {_type_name(actual)}")
        return errors
    
    for field, expected_type in schema.items():
        if field not in actual:
            errors.append(f"{path}.{field}: missing field")
            continue
        
        val = actual[field]
        exp_type = type_map.get(expected_type)
        
        if exp_type is None:
            errors.append(f"{path}.{field}: unknown type '{expected_type}'")
            continue
        
        if not isinstance(val, exp_type):
            errors.append(f"{path}.{field}: expected {expected_type}, got {_type_name(val)}")
    
    return errors


def assert_schema(actual, schema: dict, msg=""):
    """
    Assert that actual data matches the expected schema.
    Raises AssertionError with Rich output if validation fails.
    """
    errors = check_schema(actual, schema)
    
    if not errors:
        return True
    
    console.print()
    console.rule("[bold red]SCHEMA VALIDATION FAILED[/bold red]", style="red")
    
    if msg:
        console.print(f"[bold]{msg}[/bold]")
    
    table = Table(box=box.SIMPLE, show_header=True)
    table.add_column("Error", style="red")
    
    for err in errors:
        table.add_row(err)
    
    console.print(table)
    console.print()
    console.rule(style="red")
    
    raise AssertionError(f"Schema validation failed: {len(errors)} error(s)")
