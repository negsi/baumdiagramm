import random
import string


def _random_label(prefix: str | None = None) -> str:
    """
    Generate a simple random label, optionally prefixed.
    """
    core = "".join(random.choices(string.ascii_letters, k=6))
    return f"{prefix} {core}" if prefix else core


def generate_random_tree_json(
    max_depth: int = 5,
    max_children: int = 4,
    min_children: int = 0,
    prefix: str = "Node",
) -> dict:
    """
    Generate a random tree structure compatible with tree-import-json.

    Parameters
    ----------
    max_depth:
        Maximum depth of the tree (root is depth 1).
    max_children:
        Maximum number of children per node.
    min_children:
        Minimum number of children per node (except at max depth).
    prefix:
        Prefix used for node values.

    Returns
    -------
    dict
        A JSON-serializable dictionary with keys:
        - "value": str
        - "children": list[dict]
    """

    def build_node(depth: int) -> dict:
        value = _random_label(prefix)
        if depth >= max_depth:
            # Leaf node
            return {"value": value, "children": []}

        # Decide how many children this node will have
        child_count = random.randint(min_children, max_children)
        children = [build_node(depth + 1) for _ in range(child_count)]

        return {"value": value, "children": children}

    return build_node(depth=1)
