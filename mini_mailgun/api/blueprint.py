"""
Blueprint module contains all the api routes.
"""
import logging
import json

from celery import chain
from flask import Blueprint, request, abort

from mini_mailgun.api.app import get_db
from mini_mailgun.api.models import Email
from mini_mailgun.api.tasks import send_message, update_attempts, update_status
from mini_mailgun.api.tasks import find_smtp_host
from mini_mailgun.common import utc_time
from mini_mailgun.constants import STATUS_SENDING, STATUS_DELETED,  API_LOGGER
from mini_mailgun.api.schema import validate_send_email

v1_api = Blueprint('v1_api', __name__)
db = get_db()
LOG = logging.getLogger(API_LOGGER)


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
    validate_send_email(content)
    email = Email(content['from_addr'],
                  content['to_addr'],
                  content['subject'],
                  content['body'])
    db.session.add(email)
    db.session.commit()
    chain(update_attempts.s(email.uuid, email.attempts),
          find_smtp_host.s(email.to_addr),
          send_message.s(email.from_addr, email.to_addr, email.to_msg()),
          update_status.s(email.uuid)).apply_async()
    LOG.info('Email: {0} submitted to celery.'.format(email.uuid))
    return email.to_json(), 202


@v1_api.route('/v1/email/<uuid>', methods=['DELETE'])
def delete_email(uuid):
    """
    Delete an email. If it has not already been sent or is not failed.
    """
    LOG.info('Attempting to delete Email: {0}.'.format(uuid))
    email = Email.query.filter_by(uuid=uuid).first_or_404()
    if email.status != STATUS_SENDING:
        LOG.info(('Email is unable to be '
                  'deleted, is has already {0}.').format(email.status))
        abort(409)
    email.deleted_at = utc_time()
    email.status = STATUS_DELETED
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
    Return a list of emails. Defaults to 1000 max and supports offsets.
    """
    limit = request.args.get('limit', default=1000)
    offset = request.args.get('offset', default=0)
    LOG.info('Generating list of {0} emails offset at {1}.'.format(limit,
                                                                   offset))
    uuids = [uuid[0] for uuid in db.session.query(
        Email.uuid).limit(limit).offset(offset).all()]
    return json.dumps(uuids), 200
