from flask import current_app
from typing import cast
from .types import DebuggableFlask

def d(*args, **kwargs):
    """
    Global debug shortcut.

    This function provides a single, convenient entry point for invoking the
    application's debug helper. In development mode, the Flask application
    instance exposes a dynamically attached attribute `d`, which refers to the
    Rich-powered debug function. In production, this attribute does not exist.

    Behavior:
    - If the current Flask application defines a `.d` attribute, the call is
      forwarded to that debug helper.
    - If the attribute is absent (e.g., in production), the function becomes
      a no-op and silently returns.
    
    Notes:
    - The cast to `DebuggableFlask` is used only to satisfy static type checkers
      such as Pylance. At runtime, the function relies solely on the presence
      of the attribute.
    - This wrapper allows developers to write concise, one-line debug calls
      throughout the codebase without repeating type casts or hasattr checks.
    """
    if hasattr(current_app, "d"):
        cast(DebuggableFlask, current_app).d(*args, **kwargs)
