import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """
    Base configuration class shared across all application environments.

    This class centralizes all configuration values that are common to
    development, testing, and production. Environment‑specific subclasses
    extend or override these defaults as needed.

    Environment Variables
    ---------------------
    DATABASE_URL : str
        Connection string for the SQLAlchemy database engine.
    SQLALCHEMY_TRACK_MODIFICATIONS : bool
        Enables or disables SQLAlchemy's event system for object tracking.
        Defaults to False for performance reasons.
    SQLALCHEMY_ECHO : bool
        If True, SQLAlchemy logs all generated SQL statements.
    SQLALCHEMY_ENGINE_POOL_PRE_PING : bool
        Enables connection health checks before each use.
    SQLALCHEMY_ENGINE_POOL_RECYCLE : int
        Maximum lifetime (in seconds) of a DB connection before recycling.
    SQLALCHEMY_ENGINE_POOL_SIZE : int
        Size of the SQLAlchemy connection pool.
    SQLALCHEMY_ENGINE_MAX_OVERFLOW : int
        Maximum number of connections SQLAlchemy may open beyond the pool size.

    Notes
    -----
    - All values are loaded from environment variables via python‑dotenv.
    - Subclasses may override any attribute to customize behavior.
    - `init_app` is provided for extensions that require app‑level initialization.
    """

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"
    )
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == "True"

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": os.getenv("SQLALCHEMY_ENGINE_POOL_PRE_PING", "True") == "True",
        "pool_recycle": int(os.getenv("SQLALCHEMY_ENGINE_POOL_RECYCLE", 280)),
        "pool_size": int(os.getenv("SQLALCHEMY_ENGINE_POOL_SIZE", 5)),
        "max_overflow": int(os.getenv("SQLALCHEMY_ENGINE_MAX_OVERFLOW", 10)),
    }

    @staticmethod
    def init_app(app):
        """
        Hook for environment‑specific initialization.

        Subclasses may override this method to attach debugging tools,
        logging handlers, or other environment‑dependent extensions.
        """
        pass


class DevelopmentConfig(BaseConfig):
    """
    Configuration for the development environment.

    Enables debugging features and attaches the internal debug helper
    to the Flask application instance for interactive inspection.
    """

    DEBUG = True

    @staticmethod
    def init_app(app):
        from app.debug import debug
        app.d = debug


class ProductionConfig(BaseConfig):
    """
    Configuration for the production environment.

    Disables debugging and SQL echoing to ensure performance and security.
    """

    DEBUG = False
    SQLALCHEMY_ECHO = False

    @staticmethod
    def init_app(app):
        """
        Production‑specific initialization hook.

        Can be extended to configure logging, monitoring, or security
        integrations (e.g., Sentry, Prometheus).
        """
        pass


class TestingConfig(BaseConfig):
    """
    Configuration for the testing environment.

    Uses an in‑memory SQLite database for fast, isolated test execution.
    Disables engine pooling to avoid unnecessary overhead in tests.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}

    @staticmethod
    def init_app(app):
        """
        Testing‑specific initialization hook.

        Can be extended to register mock services or disable background tasks.
        """
        pass
