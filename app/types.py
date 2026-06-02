from flask import current_app
from typing import Protocol, Callable, Any, cast

# DebuggableFlask is a structural type (a "protocol") that describes
# any object which has a single attribute `d` with a specific callable shape.
#
# We use a Protocol instead of a concrete base class because:
# - We don't want (or can't) change Flask's actual class hierarchy.
# - We only care that the object *behaves like* something that has `.d`,
#   not what it inherits from.
#
# In other words: if an object has an attribute `d` that matches this
# signature, it is considered compatible with DebuggableFlask.

class DebuggableFlask(Protocol):
    # `d` is an attribute, not a method definition here.
    # We describe its *type* as a callable:
    #
    # - Callable[..., Any] means:
    #   - It can take any number and kind of positional/keyword arguments (`...`).
    #   - It can return any type (`Any`), because we don't care about the return
    #     value in this debugging context.
    #
    # This matches your `debug` helper, which is flexible in its parameters and
    # is used only for its side effects (printing, logging, etc.).
    d: Callable[..., Any]

def debug_app() -> DebuggableFlask:
    """
    Return the current Flask application instance cast to DebuggableFlask.

    This centralizes the type cast so that Pylance understands that the
    application object provides the `.d` debug helper attribute in
    development mode.
    """
    return cast(DebuggableFlask, current_app)