"""
JSON Schema module
"""
from flask import abort
from jsonschema import validate, FormatChecker

send_email = {'$schema': 'http://json-schema.org/draft-04/schema#',
              'title': 'send_email',
              'type': 'object',
              'minProperties': 4,
              'maxProperties': 4,
              'properties':
                  {'from_addr': {'type': 'string',
                                 'format': 'email',
                                 'maxLength': 256},
                   'to_addr': {'type': 'string',
                               'format': 'email',
                               'maxLength': 256},
                   'subject': {'type': 'string',
                               'maxLength': 78},
                   'body': {'type': 'string'}},
              'required': ['to_addr', 'from_addr', 'subject', 'body']}


def validate_send_email(data):
    """
    Validate send_email payload based of JSON schema def.
    Args:
        data (dict) JSON payload for request.
    Raises:
        (jsonschema.ValidationError) When payload is not valid.
    """
    try:
        validate(data, send_email, format_checker=FormatChecker())
    except:
        abort(400)
