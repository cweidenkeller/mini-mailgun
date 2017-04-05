"""
Run the API server!
"""
from gevent.wsgi import WSGIServer
from gevent import monkey

from mini_mailgun.api.app import create_app, create_logger
from mini_mailgun.constants import API_LOGGER


def run_server():
    """
    Entry point to start the API Server.
    """
    monkey.patch_all()
    app = create_app()
    logger = create_logger(API_LOGGER)
    logger.info("Starting API SERVER")
    ws = WSGIServer((app.config['APPLICATION_INTERFACE'],
                     app.config['APPLICATION_PORT']), app)
    ws.serve_forever()
