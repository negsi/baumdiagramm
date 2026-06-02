class DomainError(Exception):
    """
    Base class for all domain-level exceptions in the Application system.

    This exception type anchors the domain error hierarchy. All custom
    domain-related errors inherit from this class, allowing callers to
    catch domain-specific failures in a unified way without mixing them
    with infrastructure or framework exceptions.
    """
    pass


class NotFoundError(DomainError):
    """
    Raised when a requested domain entity cannot be located.

    Typical use cases:
    - Repository lookups that return no result.
    - Service-layer operations referencing missing IDs.
    - Attempts to access related entities that do not exist.

    This error signals that the absence of the entity is a valid domain
    condition, not a system failure.
    """
    pass


class ValidationError(DomainError):
    """
    Raised when an operation violates business rules or entity invariants.

    Examples:
    - Creating or updating an entity with invalid or missing fields.
    - Violating domain constraints (e.g., empty names, invalid URLs).
    - Attempting operations that break consistency rules.

    This error is used throughout the domain layer to enforce correctness
    and prevent invalid state transitions.
    """
    pass


class LLMError(DomainError):
    """
    Raised when an LLM (Large Language Model) operation fails.

    This includes:
    - Provider API failures.
    - Misconfigured requests.
    - Unexpected response formats.
    - Missing dependencies for provider integrations.

    By treating LLM failures as domain errors, the system can handle them
    consistently with other domain-level exceptions.
    """
    pass
