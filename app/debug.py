from rich.pretty import pprint
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from rich import inspect
from rich.traceback import Traceback

console = Console()


def _sa_to_dict(obj):
    """
    Convert a SQLAlchemy model instance into a clean, serializable dictionary.

    This helper extracts only public attributes from an ORM object by filtering
    out SQLAlchemy‑internal fields (those starting with an underscore). It is
    used to normalize model instances before printing, converting them into a
    structure that can be rendered as JSON, tables, or pretty‑printed output.

    Parameters
    ----------
    obj : Any
        A SQLAlchemy model instance or any object with a __dict__ attribute.

    Returns
    -------
    dict | Any
        A dictionary of public attributes, or the original object if it does
        not expose a __dict__.
    """
    if not hasattr(obj, "__dict__"):
        return obj
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


def debug(obj, label=None, *, json=False, table=False, inspect_obj=False):
    """
    Universal debug helper for structured, readable console output.

    This function provides a unified debugging interface built on top of the
    Rich library. It supports multiple output modes—pretty printing, JSON
    rendering, table formatting, object inspection, and exception tracebacks.
    It is designed to make debugging within Pression fast, expressive, and
    visually clear.

    Parameters
    ----------
    obj : Any
        The object to debug. May be a Python object, SQLAlchemy model instance,
        list of model instances, dictionary, or exception.
    label : str, optional
        Optional section header rendered as a Rich console rule.
    json : bool, optional
        If True, render the object as JSON using Rich's JSON renderer.
    table : bool, optional
        If True and the object is a list of dictionaries, render it as a table.
    inspect_obj : bool, optional
        If True, use Rich's introspection tools to inspect methods and attributes.

    Behavior
    --------
    - Exceptions are rendered with full tracebacks and local variables.
    - SQLAlchemy objects are automatically converted into dictionaries.
    - Lists of SQLAlchemy objects are normalized into lists of dictionaries.
    - JSON mode renders structured data with syntax highlighting.
    - Table mode formats lists of dictionaries into columnar output.
    - Fallback mode uses Rich's pretty printer.

    Notes
    -----
    - This helper is attached to the Flask app in development mode via
      `app.d = debug`, making it easily accessible in interactive shells.
    - It is intentionally flexible and safe to call with any object type.
    """
    if label:
        console.rule(f"[bold cyan]{label}")

    # Exception handling with full traceback
    if isinstance(obj, BaseException):
        tb = Traceback.from_exception(
            type(obj),
            obj,
            obj.__traceback__,
            show_locals=True,
            suppress=[]
        )
        console.print(tb)
        return

    # Normalize SQLAlchemy objects
    if hasattr(obj, "__dict__"):
        obj = _sa_to_dict(obj)

    # Normalize lists of SQLAlchemy objects
    if isinstance(obj, list) and len(obj) > 0 and hasattr(obj[0], "__dict__"):
        obj = [_sa_to_dict(o) for o in obj]

    # JSON rendering
    if json:
        console.print(JSON.from_data(obj))
        return

    # Table rendering for list[dict]
    if table and isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], dict):
        t = Table(show_header=True, header_style="bold magenta")

        for col in obj[0].keys():
            t.add_column(col)

        for row in obj:
            t.add_row(*[str(v) for v in row.values()])

        console.print(t)
        return

    # Object introspection
    if inspect_obj:
        inspect(obj, methods=True)
        return

    # Fallback pretty print
    pprint(obj)
