"""
Blueprint module contains all the api routes.
"""
import json

from flask import Blueprint, request, abort
from jsonschema import ValidationError

from mini_mailgun.api.app import get_db, get_logger
from mini_mailgun.api.models import Email
from mini_mailgun.api.tasks import send_message
from mini_mailgun.common import utc_time
from mini_mailgun.api.schema import validate_send_email

v1_api = Blueprint('v1_api', __name__)
db = get_db()
LOG = get_logger(__name__)


@v1_api.route('/v1/email', methods=['POST'])
def send_email():
    """
    Create an email.
    Example json body:
        {"from_addr": "bob@example.com",
         "to_addr": "terry@example.com",
         "subject": "Hey dude!",
         "body": "Where is my money!"}
    """
    LOG.info('Attempting to schedule an email.')
    content = request.get_json()
    # Bug in flask test client. the behavior of get_json changes
    # between the test client and the actual app.
    if not isinstance(content, dict):
        content = json.loads(content)
    try:
        LOG.info('Validating request info.')
        validate_send_email(content)
    except ValidationError:
        LOG.info(('Information not valid does not pass schema check. '
                  'From Addr: {0} To Addr: {1} '
                  'Subject: {2} Body: {3}').format(content.get('from_addr'),
                                                   content.get('to_addr'),
                                                   content.get('subject'),
                                                   content.get('body')))
        abort(400)
    from_addr = content['from_addr']
    to_addr = content['to_addr']
    subject = content['subject']
    body = content['body']
    email = Email(from_addr, to_addr, subject, body)
    db.session.add(email)
    db.session.commit()
    send_message.delay(email.uuid)
    LOG.info('Email: {0} submitted to celery.'.format(email.uuid))
    return email.to_json(), 201


@v1_api.route('/v1/email/<uuid>', methods=['DELETE'])
def delete_email(uuid):
    """
    Delete an email. If it has not already been sent or is not failed.
    """
    LOG.info('Attempting to delete Email: {0}.'.format(uuid))
    email = Email.query.filter_by(uuid=uuid).first_or_404()
    if email.status != 'SENDING':
        LOG.info(('Email is unable to be '
                  'deleted, is has already {0}.').format(email.status))
        abort(409)
    email.deleted_at = utc_time()
    db.session.commit()
    LOG.info('Email: {0} is deleted.'.format(uuid))
    return '', 200


@v1_api.route('/v1/email/<uuid>', methods=['GET'])
def get_email(uuid):
    """
    Get information about an existing email.
    """
    LOG.info('Attempting to find Email: {0}.'.format(uuid))
    email = Email.query.filter_by(uuid=uuid).first_or_404()
    LOG.info('Email: {0} found.'.format(uuid))
    return email.to_json(), 200


@v1_api.route('/v1/email', methods=['GET'])
def get_emails():
    """
    Get a list of all emails.
    """
    LOG.info('Generating list of all emails.')
    uuids = [uuid[0] for uuid in db.session.query(Email.uuid).all()]
    return json.dumps(uuids), 200
