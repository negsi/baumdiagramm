from flask import current_app
from werkzeug.exceptions import HTTPException
from typing import cast
from app.types import DebuggableFlask


def register_error_handlers(app):
    """
    Register global error handlers for the Flask application.

    This function installs a universal exception handler that catches all
    uncaught exceptions during request processing. It distinguishes between
    HTTPException instances (which Flask should return as-is) and unexpected
    internal errors. For non‑HTTP exceptions, it optionally uses the custom
    development debug helper—if available—to render structured diagnostic
    output before re‑raising the exception.

    Purpose
    -------
    - Provide a single, centralized place for handling unexpected errors.
    - Preserve normal Flask behavior for HTTPException subclasses.
    - Integrate with the Rich‑powered debug helper in development mode.
    - Ensure that exceptions are still propagated so Flask’s default
      error machinery or Werkzeug’s debugger can handle them.

    Behavior
    --------
    - If the exception is an HTTPException, it is returned unchanged.
    - If the app has a `.d` attribute (set in DevelopmentConfig), the
      debug helper is invoked to print a formatted traceback.
    - The exception is then re‑raised to allow Flask to continue its
      normal error handling flow.

    Notes
    -----
    - This handler does not swallow exceptions; it enhances visibility
      while preserving correct HTTP semantics.
    - In production, `.d` is not attached, so exceptions pass through
      without debug output.
    """

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Let Flask handle HTTP exceptions normally
        if isinstance(e, HTTPException):
            return e

        # Use the custom debug helper if initialized (development mode)
        if hasattr(current_app, "d"):
            app_with_debug = cast(DebuggableFlask, current_app)
            app_with_debug.d(e, "Uncaught Exception")

        # Re-raise so Flask/Werkzeug can continue processing
        raise e
