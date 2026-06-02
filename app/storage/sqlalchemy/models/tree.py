from app.storage.sqlalchemy.db import db
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4


class NodeDb(db.Model):
    """
    ORM model representing a single node in a hierarchical tree.

    This table stores only the intrinsic properties of a node:
    - a unique identifier
    - a value/payload
    - an optional direct parent reference (for convenience)

    Notes
    -----
    - The parent_id column is *not* used to compute the tree structure.
      The actual hierarchy is represented entirely by the closure table
      (TreePathDb). The parent_id exists only as a convenience shortcut
      for quick lookups and UI rendering.
    - The created_at timestamp is optional metadata and not required for
      the closure-table algorithm.
    """

    __tablename__ = "nodes"

    # Globally unique identifier for the node (UUID stored as string).
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))

    # Application-specific payload or label.
    value = db.Column(db.String, nullable=False)

    # Optional creation timestamp for auditing or ordering.
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Convenience reference to the direct parent node.
    # Not required for closure-table logic.
    parent_id = db.Column(db.String, db.ForeignKey("nodes.id"), nullable=True)

    # Self-referential relationship for parent → children navigation.
    parent = relationship("NodeDb", remote_side=[id], backref="children")


class TreePathDb(db.Model):
    """
    ORM model representing a single ancestor–descendant relationship
    in a hierarchical tree, following the Closure Table pattern.

    Each row describes one directed path between two nodes:
    - ancestor_id: the ancestor node
    - descendant_id: the descendant node
    - depth: number of edges between them
        * 0 = node is its own ancestor
        * 1 = direct parent–child relationship
        * 2+ = indirect ancestry
    - weight: optional edge weight for the relationship

    Notes
    -----
    - The closure table allows efficient subtree, ancestor, and path queries.
    - Weight is stored per relationship and can represent cost, confidence,
      relevance, or any other domain-specific metric.
    """

    __tablename__ = "tree_paths"

    # Ancestor node in the relationship.
    ancestor_id = db.Column(String, ForeignKey("nodes.id"), primary_key=True)

    # Descendant node in the relationship.
    descendant_id = db.Column(String, ForeignKey("nodes.id"), primary_key=True)

    # Number of edges between ancestor and descendant.
    depth = db.Column(db.Integer, nullable=False)

    # Optional weight for this relationship (e.g., cost or relevance).
    weight = db.Column(Float, nullable=True)

    # ORM relationships for convenient navigation.
    ancestor = relationship("NodeDb", foreign_keys=[ancestor_id])
    descendant = relationship("NodeDb", foreign_keys=[descendant_id])
