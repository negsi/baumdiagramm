from app.repositories.tree_repository import TreeRepository
from app.domain.tree import TreeNode


class TreeService:
    """
    High-level domain service for working with hierarchical trees stored using
    the Closure Table pattern.

    This service provides a clean, domain-focused API for tree operations while
    delegating all persistence concerns to the TreeRepository. It acts as the
    orchestration layer between controllers (or other application components)
    and the underlying repository.

    Responsibilities
    ----------------
    - Expose expressive, intention-revealing methods for tree manipulation.
    - Keep controllers free from persistence logic and SQLAlchemy details.
    - Ensure that domain rules and invariants can be enforced in one place.
    - Provide a stable abstraction over the repository layer.

    Notes
    -----
    - The service returns domain models (TreeNode), not ORM entities.
    - The service does not manage transactions; the repository handles commits.
    - Additional domain logic (validation, invariants, policies) can be added
      here without affecting the repository.
    """

    def __init__(self, tree_repository: TreeRepository):
        """
        Initialize the TreeService with its required repository dependency.

        Parameters
        ----------
        tree_repository:
            The repository responsible for all persistence operations related
            to nodes and closure-table paths.
        """
        self._repo = tree_repository

    def create_node(self, value: str, parent_id: str | None = None) -> TreeNode:
        """
        Create a new node in the tree.

        Parameters
        ----------
        value:
            The payload or label of the new node.
        parent_id:
            Optional ID of the parent node. If None, the new node becomes a root.

        Returns
        -------
        TreeNode
            The newly created domain node.
        """
        return self._repo.add_node(value=value, parent_id=parent_id)

    def get_subtree(self, node_id: str) -> list[TreeNode]:
        """
        Retrieve the entire subtree rooted at the given node.

        Parameters
        ----------
        node_id:
            The ID of the root node of the subtree.

        Returns
        -------
        list[TreeNode]
            All nodes in the subtree, including the root.
        """
        return self._repo.get_subtree(node_id)

    def get_ancestors(self, node_id: str) -> list[TreeNode]:
        """
        Retrieve all ancestor nodes of the given node.

        Parameters
        ----------
        node_id:
            The ID of the node whose ancestors should be returned.

        Returns
        -------
        list[TreeNode]
            All ancestor nodes, ordered arbitrarily.
        """
        return self._repo.get_ancestors(node_id)

    def get_root_nodes(self) -> list[TreeNode]:
        """
        Retrieve all root nodes in the tree.

        Returns
        -------
        list[TreeNode]
            All nodes without a parent.
        """
        return self._repo.get_root_nodes()

    def delete_node(self, node_id: str) -> None:
        """
        Delete a node and all closure-table paths referencing it.

        Parameters
        ----------
        node_id:
            The ID of the node to delete.

        Notes
        -----
        This operation does not automatically delete or re-parent descendants.
        If the node has children, callers must ensure that this behavior is
        acceptable or implement additional logic at the service level.
        """
        self._repo.delete_node(node_id)

    def move_node(self, node_id: str, new_parent_id: str | None) -> None:
        """
        Move a node (and its entire subtree) under a new parent.

        Parameters
        ----------
        node_id:
            The ID of the node to move.
        new_parent_id:
            The ID of the new parent node, or None to make the node a root.

        Notes
        -----
        This operation rebuilds all closure-table paths for the subtree.
        """
        self._repo.move_node(node_id, new_parent_id)

    def get_node(self, node_id):
        """
        Return a single node by its ID.

        This method provides a clean abstraction for retrieving a node from
        the repository layer. It returns None if the node does not exist.
        """
        return self._repo.get_node(node_id)

    def build_ascii_tree(self, root_id):
        """
        Build an ASCII representation of the subtree rooted at root_id.
        """
        nodes = self.get_subtree(root_id)
        if not nodes:
            return None

        # Map: parent_id -> list of children
        children_map = {}
        for n in nodes:
            children_map.setdefault(n.parent_id, []).append(n)

        # Sort children alphabetically for stable output
        for key in children_map:
            children_map[key].sort(key=lambda x: x.value)

        root = next(n for n in nodes if n.id == root_id)

        def render(node, prefix="", is_last=True):
            line = prefix
            if prefix:
                line += "└─ " if is_last else "├─ "
            line += node.value

            lines = [line]

            child_list = children_map.get(node.id, [])
            for i, child in enumerate(child_list):
                last = (i == len(child_list) - 1)
                new_prefix = prefix + ("   " if is_last else "│  ")
                lines.extend(render(child, new_prefix, last))

            return lines

        return "\n".join(render(root))

    def export_subtree_json(self, root_id):
        """
        Export the subtree rooted at root_id as a hierarchical JSON structure.
        """
        nodes = self.get_subtree(root_id)
        if not nodes:
            return None

        # Build lookup: id -> node
        node_map = {n.id: n for n in nodes}

        # Build children map
        children_map = {}
        for n in nodes:
            children_map.setdefault(n.parent_id, []).append(n)

        # Sort children alphabetically for stable output
        for key in children_map:
            children_map[key].sort(key=lambda x: x.value)

        root = node_map[root_id]

        def build(node):
            return {
                "id": node.id,
                "value": node.value,
                "children": [build(child) for child in children_map.get(node.id, [])]
            }

        return build(root)

    def import_subtree_json(self, data: dict, parent_id: str | None = None) -> str:
        """
        Import a hierarchical JSON structure and create the corresponding tree nodes.

        Parameters
        ----------
        data:
            A dictionary representing a node in the JSON tree. Expected keys:
                - "value": str
                - "children": list of child node dicts
        parent_id:
            The ID of the parent node under which the imported subtree will be attached.
            If None, the imported node becomes a root.

        Returns
        -------
        str
            The ID of the newly created root node of this imported subtree.

        Behavior
        --------
        - Creates a new node using the repository's add_node() method.
        - Recursively imports all children.
        - Returns the ID of the created node so callers can attach further structure.
        """
        # 1. Create the node itself
        node = self._repo.add_node(
            value=data["value"],
            parent_id=parent_id
        )

        # 2. Recursively import children
        for child in data.get("children", []):
            self.import_subtree_json(child, parent_id=node.id)

        return node.id

    def find_nodes(self, query: str) -> list[TreeNode]:
        """
        Search for nodes whose value contains the given query string.

        This method delegates the lookup to the repository and returns
        domain-level TreeNode objects.
        """
        return self._repo.find_by_value(query)

    def get_stats(self, root_id: str) -> dict:
        """
        Compute structural statistics for the subtree rooted at root_id.

        Returns a dictionary containing:
            - node_count: total number of nodes in the subtree
            - depth: maximum depth (root = depth 0)
            - leaf_count: number of nodes without children
            - max_branching: maximum number of direct children of any node
        """
        # Load subtree nodes
        nodes = self._repo.get_subtree(root_id)
        node_ids = {n.id for n in nodes}

        # Load closure-table paths for depth calculation
        paths = self._repo.get_subtree_paths(root_id)

        # Compute depth (max depth among paths)
        depth = max((p.depth for p in paths), default=0)

        # Compute children per node
        children_map = {nid: 0 for nid in node_ids}
        for n in nodes:
            if n.parent_id in children_map:
                children_map[n.parent_id] += 1

        leaf_count = sum(1 for nid, c in children_map.items() if c == 0)
        max_branching = max(children_map.values(), default=0)

        return {
            "node_count": len(nodes),
            "depth": depth,
            "leaf_count": leaf_count,
            "max_branching": max_branching,
        }

    def export_subtree_dot(self, root_id: str) -> str:
        """
        Export the subtree rooted at root_id as a Graphviz DOT graph.

        The output is a directed graph where each node is represented by its
        value and ID, and edges represent parent → child relationships.

        Parameters
        ----------
        root_id:
            The ID of the subtree root to export.

        Returns
        -------
        str
            A DOT-formatted string representing the subtree.
        """
        nodes = self._repo.get_subtree(root_id)

        # Build lookup: id -> node
        node_map = {n.id: n for n in nodes}

        # Build children map
        children_map = {n.id: [] for n in nodes}
        for n in nodes:
            if n.parent_id in children_map:
                children_map[n.parent_id].append(n.id)

        # Start DOT graph
        lines = []
        lines.append("digraph Tree {")
        lines.append('  node [shape=box, fontname="Arial"];')

        # Emit node labels
        for n in nodes:
            label = f"{n.value}\\n({n.id})"
            lines.append(f'  "{n.id}" [label="{label}"];')

        # Emit edges
        for parent_id, child_ids in children_map.items():
            for child_id in child_ids:
                lines.append(f'  "{parent_id}" -> "{child_id}";')

        lines.append("}")

        return "\n".join(lines)

    def generate_and_import_random_tree(
        self,
        max_depth: int = 5,
        max_children: int = 4,
        min_children: int = 0,
        prefix: str = "Node"
    ) -> str:
        """
        Generate a random tree structure and immediately import it into the database.

        Returns
        -------
        str
            The ID of the newly created root node.
        """
        from app.domain.tree_random import generate_random_tree_json

        data = generate_random_tree_json(
            max_depth=max_depth,
            max_children=max_children,
            min_children=min_children,
            prefix=prefix,
        )

        # Reuse the existing JSON import logic
        return self.import_subtree_json(data)
    
    def validate_tree(self) -> dict:
        """
        Validate consistency between NodeDb and TreePathDb.

        This method performs ONLY logic.
        It does NOT modify the database.
        It uses ONLY repository methods to read data.
        """
        nodes = self._repo.get_all_nodes()
        paths = self._repo.get_all_paths()

        node_ids = {n.id for n in nodes}

        # Indexes
        self_paths = set()
        parent_paths = set()
        zombie_paths = []
        cycles = []

        for p in paths:
            # Zombie paths: reference missing nodes
            if p.ancestor_id not in node_ids or p.descendant_id not in node_ids:
                zombie_paths.append(p)

            # Self paths
            if p.ancestor_id == p.descendant_id:
                if p.depth == 0:
                    self_paths.add(p.ancestor_id)
                else:
                    cycles.append(p)

            # Parent paths (depth=1)
            if p.depth == 1:
                parent_paths.add((p.ancestor_id, p.descendant_id))

        # Missing self paths
        missing_self = [nid for nid in node_ids if nid not in self_paths]

        # Missing parent paths
        missing_parent = []
        for n in nodes:
            if n.parent_id and (n.parent_id, n.id) not in parent_paths:
                missing_parent.append((n.parent_id, n.id))

        return {
            "missing_self_paths": missing_self,
            "zombie_paths": [
                (p.ancestor_id, p.descendant_id, p.depth) for p in zombie_paths
            ],
            "missing_parent_paths": missing_parent,
            "cycles": [
                (p.ancestor_id, p.descendant_id, p.depth) for p in cycles
            ],
        }
