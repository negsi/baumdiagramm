from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TreeNode:
    """
    Domain representation of a single node in a hierarchical tree.

    This model is intentionally independent of any persistence or ORM layer.
    It captures only the essential semantic properties of a node:
    - a stable identifier
    - the node's payload/value
    - an optional reference to its direct parent

    The actual tree structure (all ancestor/descendant relationships) is
    represented separately via TreePath, which allows us to use patterns
    like Closure Tables without polluting the node model.
    """

    # Globally unique identifier of the node (e.g. UUID as string).
    id: str

    # Application-specific payload or label for this node.
    value: str

    # ID of the direct parent node, or None if this is a root node.
    parent_id: Optional[str] = None

    # Creation timestamp for the node (optional, can be set by the repository).
    created_at: datetime | None = None


@dataclass
class TreePath:
    """
    Domain representation of a single ancestor–descendant relationship
    in a tree, following the Closure Table pattern.

    Each instance describes one directed path segment between an ancestor
    and a descendant, together with:
    - the distance between them (depth)
    - an optional edge weight (e.g. cost, confidence, relevance)

    Notes
    -----
    - depth = 0 means ancestor_id == descendant_id (the node itself).
    - depth = 1 represents a direct parent–child edge.
    - Higher depths represent indirect ancestry.
    - weight is stored on the relationship, not on the node, so that
      different paths can carry different semantics or costs.
    """

    # ID of the ancestor node in the relationship.
    ancestor_id: str

    # ID of the descendant node in the relationship.
    descendant_id: str

    # Number of edges between ancestor and descendant.
    # 0 = same node, 1 = direct parent, 2+ = indirect ancestor.
    depth: int

    # Optional weight for this ancestor–descendant relationship.
    # Can be used for costs, scores, confidence, or any edge metric.
    weight: float | None = None
