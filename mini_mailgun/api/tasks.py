"""
Celery tasks.
"""
from celery import Celery

from mini_mailgun.api.app import get_db, create_app, get_logger
from mini_mailgun.api.models import Email
from mini_mailgun.common import utc_time
from mini_mailgun.smtp.client import Client


db = get_db()
LOG = get_logger(__name__)


def make_celery(app):
    """
    Construct a celery app and tie it into the flask app context.
    Args:
        app (flask.flask): A instantiated flask app.
    Kwargs:
        None
    Raises:
        None
    Returns:
        (celery.Celery): A celery app with a modified taskbase to allow
            access to the flask app context.
    """
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app = create_app(register_blueprint=False)
celery_app = make_celery(app)


@celery_app.task(bind=True)
def send_message(self, uuid):
    """
    Async task to send email messages.
    Args:
        uuid (str): UUID of the email message.
    Kwargs:
        None
    Raises:
        None
    Returns:
        None
    """
    LOG.info('Attempting to send Email: {0}'.format(uuid))
    email = Email.query.filter_by(uuid=uuid).first()
    if email.deleted_at or email.attempts >= app.config['MAX_RETRIES']:
        LOG.info(('Email: {0} is deleted and '
                  'has reached max retries.').format(uuid))
        return
    email.attempts += 1
    email.last_attempt = utc_time()
    smtp_client = Client(app.config['SMTP_HOST'],
                         app.config['SMTP_PORT'],
                         use_tls=app.config['USE_TLS'],
                         username=app.config['SMTP_AUTH_USERNAME'],
                         password=app.config['SMTP_AUTH_PASSWORD'])
    resp = smtp_client.send_message(email.to_msg())
    email.status_code = resp['code']
    LOG.info(('Email: {0} Status: {1} '
              'Response Message: {2}.').format(email.uuid,
                                               resp['code'],
                                               resp['message']))
    if resp['code'] not in range(250, 253):
        if email.attempts == app.config['MAX_RETRIES']:
            LOG.info('Email: {0} has failed to send.'.format(uuid))
            email.status = 'FAILED'
    else:
        LOG.info('Email: {0} has been sent.'.format(uuid))
        email.status = 'SENT'
    db.session.add(email)
    db.session.commit()
    smtp_client.quit()
    if email.attempts != app.config['MAX_RETRIES'] and email.status != 'SENT':
        LOG.info('Rescheduling Email: {0}'.format(uuid))
        self.retry(countdown=app.config['RETRY_WAIT'])
