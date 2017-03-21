"""
Celery tasks.
"""
from celery import Celery, chain
import dns.resolver

from mini_mailgun.api.app import get_db, create_app, create_logger
from mini_mailgun.api.models import Email
from mini_mailgun.common import utc_time
from mini_mailgun.constants import STATUS_SENT, STATUS_FAILED, STATUS_DELETED
from mini_mailgun.constants import CELERY_LOGGER
from mini_mailgun.smtp.client import Client


db = get_db()
LOG = create_logger(CELERY_LOGGER)


def make_celery(app):
    """
    Construct a celery app and tie it into the flask app context.
    Args:
        app (flask.flask): A instantiated flask app.
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


@celery_app.task(acks_late=True)
def update_attempts(uuid, attempts):
    """
    Async task to update attempts in the db.
    Args:
        uuid (str): UUID of the email message.
        attempts (int): number of attempts tried.
    """
    LOG.info('Attempting to send Email: {0}'.format(uuid))
    email = Email.query.filter_by(uuid=uuid).first()
    if email.status == STATUS_DELETED:
        raise EmailDeletedError('Email {0} deleted'.format(uuid))
    else:
        email.attempts = attempts + 1
        email.last_attempt = utc_time()
    db.session.add(email)
    db.session.commit()
    return email.attempts


@celery_app.task(acks_late=True)
def find_smtp_host(attempts, to_addr):
    LOG.info('Grabbing SMTP host for {0}'.format(to_addr))
    try:
        res = dns.resolver.query(to_addr.split('@')[1], 'MX')
    except:
        LOG.info(('No MX Records found for {0}').format(to_addr))
        return None
    mx_records = {}
    for mx in res:
        mx_records[mx.preference.real] = mx.exchange.to_text()
    while(len(mx_records) < attempts):
        attempts -= len(mx_records)
    LOG.info('Out of {0} MX records selected {1}'.format(
        len(mx_records),
        mx_records[sorted(mx_records.keys())[attempts - 1]]))
    return mx_records[sorted(mx_records.keys())[attempts - 1]]


@celery_app.task(acks_late=True)
def send_message(smtp_host, from_addr, to_addr, message):
    """
    Async task to send an email message.
    Args:
        mx_record (str) The mx record for the to_addr
        from_addr (str): The sender's address.
        to_addr (str): The recipient's address.
        message (str): A well formed email message.
    """
    if not smtp_host:
        return {'code': -1, 'message': 'No MX records for host'}
    smtp_client = Client(smtp_host,
                         app.config['SMTP_PORT'],
                         use_tls=app.config['USE_TLS'],
                         username=app.config['SMTP_AUTH_USERNAME'],
                         password=app.config['SMTP_AUTH_PASSWORD'])
    return smtp_client.send_message(from_addr, to_addr, message)


@celery_app.task(acks_late=True)
def clean_db_record(uuid):
    """
    Delete a db record.
    Args:
        uuid (str): uuid of the db record.
    """
    LOG.info('Attempting to delete record {0}'.format(uuid))
    db.session.query(Email).filter(
        Email.uuid == uuid).delete(synchronize_session=False)
    db.session.commit()
    LOG.info('DB record {0} deleted.'.format(uuid))


@celery_app.task(acks_late=True)
def update_status(resp, uuid):
    """
    Async task to update message status.
    Args:
        resp (dict): A dict containing resp code and message.
        uuid (string): The uuid of the email message.
    """
    email = Email.query.filter_by(uuid=uuid).first()
    email.status_code = resp['code']
    LOG.info(('Email: {0} Status: {1} '
              'Response Message: {2}.').format(email.uuid,
                                               resp['code'],
                                               resp['message']))
    if resp['code'] not in range(250, 253) or resp['code'] == -1:
        if email.attempts == app.config['MAX_RETRIES']:
            LOG.info('Email: {0} has failed to send.'.format(uuid))
            email.status = STATUS_FAILED
    else:
        LOG.info('Email: {0} has been sent.'.format(uuid))
        email.status = STATUS_SENT
    db.session.add(email)
    db.session.commit()
    if (email.attempts != app.config['MAX_RETRIES']
            and email.status != STATUS_SENT):
        LOG.info('Rescheduling Email: {0}'.format(uuid))
        chain(update_attempts.s(email.uuid, email.attempts),
              find_smtp_host.s(email.to_addr),
              send_message.s(email.from_addr, email.to_addr,
                             email.to_msg()),
              update_status.s(email.uuid)).apply_async(
                  countdown=app.config['RETRY_WAIT'])
    else:
        clean_db_record.s(uuid).apply_async(
            countdown=app.config['DELETE_WAIT'])
