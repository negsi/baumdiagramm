from app.storage.sqlalchemy.db import db
from app.storage.sqlalchemy.models.tree import NodeDb, TreePathDb

"""
Central export module for all SQLAlchemy ORM models and the global database
instance used throughout the Pression application.

This module acts as the single, stable import surface for the persistence
layer. By re‑exporting all mapped models and the shared SQLAlchemy `db`
instance from one place, the rest of the application can avoid deep or
brittle import paths and remain decoupled from the internal directory
structure of the ORM layer.

Purpose
-------
- Provide a unified import location for all ORM models.
- Ensure that SQLAlchemy’s metadata discovery works consistently by exposing
  all mapped classes in one module.
- Keep repositories, services, and migrations independent of file layout
  changes inside the persistence layer.
- Improve maintainability by centralizing the public API of the storage
  subsystem.

Tree Models
-----------
NodeDb
    Represents a single node in the hierarchical tree.
TreePathDb
    Represents ancestor–descendant relationships using the Closure Table pattern.

Usage
-----
Instead of importing ORM models from their deep module paths:

    from app.storage.sqlalchemy.models.tree import NodeDb

you can simply write:

    from app.storage.sqlalchemy.models import NodeDb, TreePathDb, db

This keeps imports consistent and easier to maintain across the application.
"""

__all__ = [
    "db",
    "NodeDb",
    "TreePathDb",
]
