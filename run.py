from app import create_app

app = create_app()

if __name__ == "__main__":
    """
    Application entry point.

    This module serves as the executable launcher for the Flask
    application. It delegates all initialization logic to the application
    factory (`create_app`), ensuring that configuration, extensions, routes,
    and error handlers are set up consistently across environments.

    Behavior
    --------
    - Imports and constructs the Flask application via the factory.
    - Runs the development server when executed directly.
    - In production, this file is typically not used; instead, a WSGI server
      such as Gunicorn or uWSGI imports the `app` object.

    Notes
    -----
    - The `app.run()` call is intended for local development only.
    - For deployment, configure a proper WSGI entry point.
    """
    app.run()
