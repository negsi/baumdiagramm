"""
MIT License
Copyright (c) 2026 Christian Siewert


"""

import os
from flask import Flask
from app.storage.sqlalchemy.db import db
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.errors import register_error_handlers


def create_app() -> Flask:
    """
    Create and configure the Flask application instance.

    This function implements the application factory pattern recommended by
    Flask for building modular, testable, and extensible applications. It
    constructs the Flask instance, loads environment‑specific configuration,
    initializes extensions, registers routes, and wires up template filters,
    context processors, and error handlers.

    Architecture Overview
    ---------------------
    Pression uses a layered architecture where:
    - Configuration is environment‑driven (development, testing, production)
    - SQLAlchemy is initialized lazily via `init_app`
    - Blueprints encapsulate route modules
    - Context processors inject UI‑level state (menu, breadcrumbs)
    - Template filters provide formatting helpers for Jinja2
    - Error handlers unify exception presentation across the app

    Behavior
    --------
    - Determines the active environment via the FLASK_ENV variable.
    - Loads the corresponding configuration class.
    - Initializes the database and creates all tables on startup.
    - Registers all blueprints that define the HTTP routes.
    - Attaches global context processors and template filters.
    - Installs centralized error handling.

    Returns
    -------
    Flask
        A fully configured Flask application instance ready to run.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    app = Flask(__name__,)

    # Select configuration class based on FLASK_ENV
    env = os.getenv("FLASK_ENV", "development").lower()

    if env == "production":
        app.config.from_object(ProductionConfig)
        ProductionConfig.init_app(app)
    elif env == "testing":
        app.config.from_object(TestingConfig)
        TestingConfig.init_app(app)
    else:
        app.config.from_object(DevelopmentConfig)
        DevelopmentConfig.init_app(app)

    # Initialize database
    db.init_app(app)

    # Create tables on startup (safe for dev/test; production may use migrations)
    with app.app_context():
        db.create_all()

    # Error handling
    register_error_handlers(app)

    return app
