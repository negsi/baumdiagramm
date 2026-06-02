from app.repositories.tree_repository import TreeRepository
from app.services.tree_service import TreeService


class Container:
    """
    Lightweight Dependency Injection container for Pression.

    This container centralizes the construction and lifetime management of
    repositories and services. It follows a lazy‑loading pattern: each
    dependency is instantiated only when first accessed, then cached for
    subsequent use.

    Purpose
    -------
    - Provide a simple and explicit DI mechanism without relying on external
      frameworks or metaprogramming.
    - Ensure that each component is created exactly once (singleton‑style).
    - Keep wiring logic out of services and repositories, allowing them to
      remain focused on domain behavior rather than construction concerns.
    - Make the dependency graph easy to understand, maintain, and test.

    Architectural Principles
    ------------------------
    - Repositories:
        Stateless, persistence‑focused components. Safe to reuse across the
        application. They encapsulate all database access logic.
    - Services:
        Contain domain logic and orchestrate repository operations. They do
        not know how dependencies are constructed; they simply receive them.
    - Lazy Loading:
        Dependencies are created only when accessed via their property.
        This avoids unnecessary initialization and ensures consistent
        instances throughout the application lifetime.

    Example
    -------
        container = Container()
        tree_service = container.tree_service
        node = tree_service.create_node("Example")
    """

    def __init__(self):
        # Internal storage for lazily instantiated components.
        self._tree_repository = None
        self._tree_service = None

    @property
    def tree_repository(self) -> TreeRepository:
        """
        Lazily instantiate and return the TreeRepository.

        The repository encapsulates all persistence logic for nodes and
        closure‑table paths. It is stateless and safe to reuse, so a single
        instance is shared across the application.
        """
        if self._tree_repository is None:
            self._tree_repository = TreeRepository()
        return self._tree_repository

    @property
    def tree_service(self) -> TreeService:
        """
        Lazily instantiate and return the TreeService.

        The service provides high‑level domain operations on the tree,
        delegating persistence to the TreeRepository. It is constructed
        only once and reused for all tree‑related operations.
        """
        if self._tree_service is None:
            self._tree_service = TreeService(
                tree_repository=self.tree_repository
            )
        return self._tree_service


# Global container instance used by the application.
container = Container()
