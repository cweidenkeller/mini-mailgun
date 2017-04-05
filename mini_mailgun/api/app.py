"""
Application odds and ends.
"""
import logging

from flask import Flask

from mini_mailgun.api.db import db


def create_app(register_blueprint=True):
    """
    Create a flask app with blueprints and a database
    Args:
        None
    Kwargs:
        register_blueprint (bool): Used to initalize celery to avoid
                                   circular imports.
    Returns:
        A flask application.
    """
    app = Flask(__name__)
    app.config.from_envvar('MINI_MAILGUN_CONFIG')
    if register_blueprint:
        from mini_mailgun.api.blueprint import v1_api
        app.register_blueprint(v1_api)
    db.init_app(app)
    return app


def get_db():
    """
    Get a database session.
    Returns:
        A flask-sqlalchemy database object.
    """
    app = Flask(__name__)
    app.config.from_envvar('MINI_MAILGUN_CONFIG')
    db.init_app(app)
    return db


def create_logger(mname):
    """
    Get a logger object.
    Args:
        mname (str): generally the __name__ of the current module.
    Returns:
        A python logger object.
    """
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    app = Flask(__name__)
    app.config.from_envvar('MINI_MAILGUN_CONFIG')
    logger = logging.getLogger(mname)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    handler = logging.FileHandler(app.config['APP_LOG'])
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
