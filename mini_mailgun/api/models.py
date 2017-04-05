"""
Database models.
"""
import json

from flanker.mime import create

from mini_mailgun.api.db import db
from mini_mailgun.common import utc_time, uuid
from mini_mailgun.constants import STATUS_SENDING


class Email(db.Model):
    """
    Email DB model.
    """
    uuid = db.Column(db.String(37), primary_key=True, unique=True)
    from_addr = db.Column(db.String(256), nullable=False)
    to_addr = db.Column(db.String(256), nullable=False)
    subject = db.Column(db.String(78), nullable=False)
    body = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    last_attempt = db.Column(db.DateTime, nullable=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default=STATUS_SENDING)
    status_code = db.Column(db.Integer, nullable=True)

    def __init__(self, from_addr, to_addr, subject, body):
        """
        Construct an email model.
        Args:
            from_addr (str): The sender's email address.
            to_addr (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The body of the message.
        """
        if not self.uuid:
            self.uuid = uuid()
        if not self.created_at:
            self.created_at = utc_time()
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.subject = subject
        self.body = body

    def to_json(self):
        """
        Get the json representation of this model. Used for sending info
        via the rest api.
        Returns:
            (str) Json representation of this DB model.
        """
        return json.dumps({'uuid': self.uuid,
                           'from_addr': self.from_addr,
                           'to_addr': self.to_addr,
                           'subject': self.subject,
                           'body': self.body,
                           'created_at': str(self.created_at),
                           'deleted_at': str(self.deleted_at),
                           'last_attempt': str(self.last_attempt),
                           'attempts': self.attempts,
                           'status': self.status,
                           'status_code': self.status_code})

    def to_msg(self):
        """
        Get a well formed email message based off of the info in this
        DB record. Used when sending the email in the tasks module.
        Returns:
            (u'str') Well formed email message.
        """
        message = create.text("plain", self.body)
        message.headers['From'] = self.from_addr
        message.headers['To'] = self.to_addr
        message.headers['Subject'] = self.subject
        return message.to_string()
