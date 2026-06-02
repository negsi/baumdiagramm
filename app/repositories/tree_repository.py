from app.domain.tree import TreeNode
from app.storage.sqlalchemy.models.tree import NodeDb, TreePathDb
from app.storage.sqlalchemy.db import db


class TreeRepository:
    """
    Repository for working with hierarchical trees stored using the Closure Table pattern.

    Responsibilities
    ----------------
    - Encapsulate all persistence logic for nodes and their ancestor–descendant paths.
    - Provide a simple API for creating, querying, moving, and deleting nodes.
    - Keep higher-level services free from SQLAlchemy and schema details.

    Design Notes
    ------------
    - NodeDb represents the actual node entity (id, value, parent_id).
    - TreePathDb represents all ancestor–descendant relationships (closure table).
    - This repository operates on domain models (TreeNode) at the boundary.
    """

    def get_node(self, node_id: str) -> TreeNode | None:
        """
        Retrieve a single node by its ID.

        This method provides a thin abstraction over the underlying persistence
        layer. It performs a direct lookup on the NodeDb table and maps the ORM
        model to a TreeNode domain object. If no record exists for the given ID,
        the method returns None instead of raising an exception.

        Parameters
        ----------
        node_id:
            The primary key of the node to retrieve.

        Returns
        -------
        TreeNode | None
            A fully populated TreeNode domain object if the node exists,
            otherwise None.
        """
        model = NodeDb.query.get(node_id)
        if not model:
            return None

        return TreeNode(
            id=model.id,
            value=model.value,
            parent_id=model.parent_id,
            created_at=model.created_at,
        )
    
    def get_subtree(self, node_id: str) -> list[TreeNode]:
        """
        Return all nodes in the subtree rooted at the given node.

        This includes the root node itself and all its descendants.

        Implementation
        --------------
        - Query all TreePathDb rows where ancestor_id == node_id.
        - Collect all descendant IDs from those paths.
        - Load the corresponding NodeDb rows.
        - Map them to TreeNode domain objects.
        """
        paths = TreePathDb.query.filter_by(ancestor_id=node_id).all()
        node_ids = [p.descendant_id for p in paths]
        nodes = NodeDb.query.filter(NodeDb.id.in_(node_ids)).all()
        return [TreeNode(id=n.id, value=n.value, parent_id=n.parent_id) for n in nodes]

    def get_subtree_paths(self, node_id: str) -> list[TreePathDb]:
        """
        Return all closure-table paths where the given node is the ancestor.
        Used for computing subtree depth and structural statistics.
        """
        return TreePathDb.query.filter_by(ancestor_id=node_id).all()

    def get_ancestors(self, node_id: str) -> list[TreeNode]:
        """
        Return all ancestor nodes of the given node (excluding the node itself).

        Implementation
        --------------
        - Query all TreePathDb rows where descendant_id == node_id.
        - Filter out the self-path (depth = 0).
        - Collect all ancestor IDs.
        - Load the corresponding NodeDb rows.
        - Map them to TreeNode domain objects.
        """
        paths = TreePathDb.query.filter_by(descendant_id=node_id).all()
        node_ids = [p.ancestor_id for p in paths if p.depth > 0]
        nodes = NodeDb.query.filter(NodeDb.id.in_(node_ids)).all()
        return [TreeNode(id=n.id, value=n.value, parent_id=n.parent_id) for n in nodes]

    def get_root_nodes(self) -> list[TreeNode]:
        """
        Return all root nodes in the tree.

        A root node is defined as a node without a direct parent
        (i.e. parent_id is NULL in the NodeDb table).
        """
        nodes = NodeDb.query.filter_by(parent_id=None).all()
        return [TreeNode(id=n.id, value=n.value, parent_id=None) for n in nodes]

    def add_node(
        self,
        value: str,
        parent_id: str | None = None,
        weight: float | None = None
    ) -> TreeNode:
        """
        Create a new node and insert all corresponding closure-table paths.

        Parameters
        ----------
        value:
            The payload or label of the new node.
        parent_id:
            The ID of the direct parent node, or None if this is a root node.
        weight:
            Optional edge weight for the direct parent → child relationship.
            This is stored only on the direct edge (depth = 1).

        Behavior
        --------
        - Inserts a new NodeDb row.
        - Adds the self-path (node → node, depth = 0).
        - If a parent is given:
          - Copies all ancestor paths from the parent to the new node
            (preserving their weights).
          - Adds the direct parent → child path with the given weight.
        """
        # Create and persist the node itself.
        node = NodeDb(value=value, parent_id=parent_id)
        db.session.add(node)
        # Flush to obtain the generated node.id before inserting paths.
        db.session.flush()

        # 1. Self-path: every node is its own ancestor at depth 0.
        db.session.add(TreePathDb(
            ancestor_id=node.id,
            descendant_id=node.id,
            depth=0,
            weight=None
        ))

        # 2. Inherit all ancestor paths from the parent, if a parent exists.
        if parent_id:
            parent_paths = TreePathDb.query.filter_by(descendant_id=parent_id).all()
            for p in parent_paths:
                if p.depth == 0:
                    # skip parent self-path → avoids duplicate (parent → child)
                    continue
                
                db.session.add(TreePathDb(
                    ancestor_id=p.ancestor_id,
                    descendant_id=node.id,
                    depth=p.depth + 1,
                    # Inherit the ancestor path's weight (if any).
                    weight=p.weight
                ))

            # 3. Add the direct parent → child edge with the provided weight.
            db.session.add(TreePathDb(
                ancestor_id=parent_id,
                descendant_id=node.id,
                depth=1,
                weight=weight
            ))

        db.session.commit()

        return TreeNode(id=node.id, value=node.value, parent_id=parent_id)

    def delete_node(self, node_id: str) -> None:
        """
        Delete a node and all associated closure-table paths.

        Behavior
        --------
        - Removes all TreePathDb rows where the node appears either as
          ancestor or descendant.
        - Removes the NodeDb row itself.
        - Commits the transaction.

        Note
        ----
        This method does not automatically re-parent or preserve descendants.
        If the node has children, their paths and node rows will remain
        inconsistent unless handled separately. In many use cases, you will
        want to delete the entire subtree instead.
        """
        # 1. Remove all paths that involve this node as ancestor or descendant.
        TreePathDb.query.filter(
            (TreePathDb.ancestor_id == node_id) |
            (TreePathDb.descendant_id == node_id)
        ).delete()

        # 2. Remove the node itself.
        NodeDb.query.filter_by(id=node_id).delete()

        db.session.commit()

    def move_node(
        self,
        node_id: str,
        new_parent_id: str | None,
        weight: float | None = None
    ) -> None:
        """
        Move a node (and its entire subtree) under a new parent.

        Parameters
        ----------
        node_id:
            The ID of the node to move (root of the subtree).
        new_parent_id:
            The ID of the new parent node, or None to make this node a root.
        weight:
            Optional edge weight for the new direct parent → child relationship.

        Behavior
        --------
        - Determines the full subtree rooted at node_id.
        - Deletes all closure-table paths that reference any node in that subtree.
        - Rebuilds:
          - self-paths for all nodes in the subtree
          - ancestor paths from the new parent (if provided)
          - the direct parent → child edge with the given weight
        - Updates the node's parent_id in NodeDb.
        """
        # 1. Determine the subtree: all descendants of node_id (including itself).
        subtree_paths = TreePathDb.query.filter_by(ancestor_id=node_id).all()
        subtree_ids = [p.descendant_id for p in subtree_paths]

        # 2. Remove all paths where any of these nodes appear as descendants.
        #    This effectively removes all ancestor relationships for the subtree.
        TreePathDb.query.filter(
            TreePathDb.descendant_id.in_(subtree_ids)
        ).delete()

        # 3. Recreate self-paths for each node in the subtree.
        for descendant in subtree_ids:
            db.session.add(TreePathDb(
                ancestor_id=descendant,
                descendant_id=descendant,
                depth=0,
                weight=None
            ))

        # 4. If a new parent is provided, attach the subtree under that parent.
        if new_parent_id:
            # Fetch all ancestor paths of the new parent.
            parent_paths = TreePathDb.query.filter_by(descendant_id=new_parent_id).all()

            # For each node in the subtree, inherit all ancestor paths
            # from the new parent, increasing depth accordingly.
            for descendant in subtree_ids:
                for p in parent_paths:
                    if p.depth == 0:
                        # Skip self-path of new parent → avoids duplicate direct edge
                        continue
                    db.session.add(TreePathDb(
                        ancestor_id=p.ancestor_id,
                        descendant_id=descendant,
                        depth=p.depth + 1,
                        weight=p.weight
                    ))

            # Add the direct new_parent → node_id edge with the given weight.
            db.session.add(TreePathDb(
                ancestor_id=new_parent_id,
                descendant_id=node_id,
                depth=1,
                weight=weight
            ))

        # 5. Update the direct parent reference on the node itself.
        node = NodeDb.query.get(node_id)
        node.parent_id = new_parent_id

        db.session.commit()

    def find_by_value(self, query: str) -> list[TreeNode]:
        """
        Find all nodes whose value contains the given query string
        (case-insensitive substring match).

        Parameters
        ----------
        query:
            The substring to search for inside node values.

        Returns
        -------
        list[TreeNode]
            All matching nodes as domain objects.
        """
        pattern = f"%{query}%"
        models = NodeDb.query.filter(NodeDb.value.ilike(pattern)).all()

        return [
            TreeNode(
                id=m.id,
                value=m.value,
                parent_id=m.parent_id,
                created_at=m.created_at,
            )
            for m in models
        ]
    
    def get_all_nodes(self) -> list[TreeNode]:
        """
        Retrieve all nodes from the database and convert them into domain-level TreeNode objects.

        This method:
        - Queries the underlying NodeDb model for all persisted nodes.
        - Maps each ORM instance (NodeDb) to a pure domain object (TreeNode).
        - Returns a list of TreeNode instances that can be used by the application
        without leaking ORM/DB-specific details into the domain layer.
        """
        return [
            TreeNode(
                id=m.id,          # Unique identifier of the node in the database
                value=m.value,    # Payload or label associated with this node
                parent_id=m.parent_id,  # ID of the parent node (or None for root nodes)
            )
            for m in NodeDb.query.all()  # Fetch all node records from the database
        ]


    def get_all_paths(self) -> list["TreePathDb"]:
        """
        Retrieve all stored paths between nodes from the database.

        This method:
        - Queries the TreePathDb model for all path records.
        - Returns the raw ORM objects (TreePathDb instances), which typically represent
        ancestor–descendant relationships in a closure table or similar structure.
        - Is useful when higher-level logic needs to analyze or reconstruct the tree
        structure based on all known paths.
        """
        return TreePathDb.query.all()  # Fetch all path records (ancestor–descendant pairs)

