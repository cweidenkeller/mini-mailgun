"""
Run the API server!
"""
from gevent.wsgi import WSGIServer
from gevent import monkey

from mini_mailgun.api.app import create_app, get_logger


def run_server():
    """
    Entry point to start the API Server.
    Args:
        None
    Kwargs:
        None
    Raises:
        None
    Returns:
        None
    """
    monkey.patch_all()
    app = create_app()
    logger = get_logger(__name__)
    logger.info("Starting API SERVER")
    ws = WSGIServer((app.config['APPLICATION_INTERFACE'],
                     app.config['APPLICATION_PORT']), app)
    ws.serve_forever()
