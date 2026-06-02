import click
import json
from functools import wraps
from app import create_app
from app.services.container import container
from app.domain.tree_random import generate_random_tree_json

# -------------------------------------------------------------------
# DECORATOR FOR APP CONTEXT
# -------------------------------------------------------------------
def with_app_context(f):
    """
    Decorator to wrap CLI commands in an application context 
    and provide standardized error handling.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        app = create_app()
        with app.app_context():
            try:
                return f(*args, **kwargs)
            except Exception as e:
                click.echo(f"Error: {e}")
                raise
    return wrapper

@click.group()
def cli():
    """Root Click command group."""
    pass

# -------------------------------------------------------------------
# TREE COMMANDS
# -------------------------------------------------------------------

@cli.command("tree-add-node")
@click.argument("value")
@click.argument("parent_id", required=False)
@with_app_context
def tree_add_node(value, parent_id):
    node = container.tree_service.create_node(value=value, parent_id=parent_id)
    click.echo(f"NODE_CREATED: {node.id} (value='{node.value}')")

@cli.command("tree-list-subtree")
@click.argument("node_id")
@with_app_context
def tree_list_subtree(node_id):
    subtree = container.tree_service.get_subtree(node_id)
    if not subtree:
        return click.echo(f"No nodes found for subtree rooted at {node_id}")
        
    click.echo(f"Subtree rooted at {node_id}:")
    for node in subtree:
        click.echo(f"- {node.id}  value='{node.value}'  parent={node.parent_id}")

@cli.command("tree-list-ancestors")
@click.argument("node_id")
@with_app_context
def tree_list_ancestors(node_id):
    ancestors = container.tree_service.get_ancestors(node_id)
    if not ancestors:
        return click.echo(f"No ancestors found for node {node_id}")
        
    click.echo(f"Ancestors of {node_id}:")
    for node in ancestors:
        click.echo(f"- {node.id}  value='{node.value}'  parent={node.parent_id}")

@cli.command("tree-list-descendants")
@click.argument("node_id")
@with_app_context
def tree_list_descendants(node_id):
    subtree = container.tree_service.get_subtree(node_id)
    descendants = [n for n in subtree if n.id != node_id]
    
    if not descendants:
        return click.echo(f"No descendants found for node {node_id}")

    click.echo(f"Descendants of {node_id}:")
    for node in descendants:
        click.echo(f"- {node.id}  value='{node.value}'  parent={node.parent_id}")

@cli.command("tree-list-roots")
@with_app_context
def tree_list_roots():
    roots = container.tree_service.get_root_nodes()
    if not roots:
        return click.echo("No root nodes found.")
    
    click.echo("Root nodes:")
    for node in roots:
        click.echo(f"- {node.id}  value='{node.value}'")

@cli.command("tree-move-node")
@click.argument("node_id")
@click.argument("new_parent_id", required=False)
@with_app_context
def tree_move_node(node_id, new_parent_id):
    container.tree_service.move_node(node_id=node_id, new_parent_id=new_parent_id)
    msg = f"Node {node_id} moved under parent {new_parent_id}" if new_parent_id else f"Node {node_id} moved to root level"
    click.echo(msg)

@cli.command("tree-delete-node")
@click.argument("node_id")
@with_app_context
def tree_delete_node(node_id):
    container.tree_service.delete_node(node_id)
    click.echo(f"Node {node_id} deleted successfully")

@cli.command("tree-print")
@click.argument("root_id")
@with_app_context
def tree_print(root_id):
    ascii_tree = container.tree_service.build_ascii_tree(root_id)
    click.echo(ascii_tree if ascii_tree else f"No subtree found for root {root_id}")

@cli.command("tree-export-json")
@click.argument("root_id")
@with_app_context
def tree_export_json(root_id):
    data = container.tree_service.export_subtree_json(root_id)
    if not data:
        return click.echo(f"No subtree found for root {root_id}")
    click.echo(json.dumps(data, indent=2))

@cli.command("tree-info")
@click.argument("node_id")
@with_app_context
def tree_info(node_id):
    node = container.tree_service.get_node(node_id)
    if not node:
        return click.echo(f"Node {node_id} not found")
        
    click.echo(f"Node details:\n  id: {node.id}\n  value: {node.value}\n  parent_id: {node.parent_id}\n  created_at: {node.created_at}")

@cli.command("tree-import-json")
@click.argument("json_file", type=click.Path(exists=True))
@click.option("--parent", "parent_id", default=None)
@with_app_context
def tree_import_json(json_file, parent_id):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_root_id = container.tree_service.import_subtree_json(data, parent_id=parent_id)
    click.echo(f"Imported subtree. New root node ID: {new_root_id}")

@cli.command("tree-find")
@click.argument("query")
@with_app_context
def tree_find(query):
    results = container.tree_service.find_nodes(query)
    if not results:
        return click.echo(f"No nodes found matching '{query}'")
    
    click.echo(f"Found {len(results)} matching nodes:")
    for node in results:
        click.echo(f"- {node.id}  value='{node.value}'  parent='{node.parent_id}'")

@cli.command("tree-stats")
@click.argument("root_id")
@with_app_context
def tree_stats(root_id):
    stats = container.tree_service.get_stats(root_id)
    click.echo(f"Statistics for subtree rooted at {root_id}:\n  Total nodes: {stats['node_count']}\n  Max depth: {stats['depth']}\n  Leaf nodes: {stats['leaf_count']}\n  Max branching: {stats['max_branching']}")

@cli.command("tree-export-dot")
@click.argument("root_id")
@with_app_context
def tree_export_dot(root_id):
    click.echo(container.tree_service.export_subtree_dot(root_id))

# Random generation commands (kept simple)
@cli.command("tree-generate-random-json")
# ... (Parameter options omitted for brevity)
def tree_generate_random_json(max_depth, max_children, min_children, prefix):
    data = generate_random_tree_json(max_depth=max_depth, max_children=max_children, min_children=min_children, prefix=prefix)
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))

@cli.command("tree-generate-random")
@with_app_context
def tree_generate_random(max_depth, max_children, min_children, prefix):
    new_root_id = container.tree_service.generate_and_import_random_tree(max_depth=max_depth, max_children=max_children, min_children=min_children, prefix=prefix)
    click.echo(f"Random tree imported. New root node ID: {new_root_id}")

@cli.command("tree-validate")
@with_app_context
def tree_validate():
    report = container.tree_service.validate_tree()
    
    click.echo("Validation report:")
    click.echo(f"  Missing self paths:      {len(report['missing_self_paths'])}")
    click.echo(f"  Zombie paths:            {len(report['zombie_paths'])}")
    click.echo(f"  Missing parent paths:    {len(report['missing_parent_paths'])}")
    click.echo(f"  Cycles (depth>0 self):   {len(report['cycles'])}")

    if report["missing_self_paths"]:
        click.echo("  Example missing self path node IDs:")
        for nid in report["missing_self_paths"][:5]:
            click.echo(f"    - {nid}")

if __name__ == "__main__":
    cli()
