from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy database instance used across the application.
# 
# This object acts as:
# - the central ORM registry,
# - the session factory,
# - and the metadata container for all mapped models.
#
# It is initialized here at module level so that:
# - models can import `db` without causing circular dependencies,
# - the application factory can later call `db.init_app(app)` to bind
#   the instance to the Flask application context.
#
# Typical usage:
#   from app.extensions import db
#   class Article(db.Model):
#       id = db.Column(db.Integer, primary_key=True)
#       ...
#
# The actual database connection is not established until the Flask
# application initializes the extension.
db = SQLAlchemy()
