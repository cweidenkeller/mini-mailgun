"""
mini_mailgun client
"""
import json

import requests

from mini_mailgun.exceptions import ClientExceptionError, ServerExceptionError
from mini_mailgun.exceptions import MessageAlreadySentOrFailedError


class Message:
    """
    Simple object to represent an email message.
    """

    def __init__(self, message_json):
        """
        Constructor for Message object.
        Args:
            message_json (dict): A dict containing the response from send_email
            or get_email.
        """
        self.uuid = message_json['uuid']
        self.from_addr = message_json['from_addr']
        self.to_addr = message_json['to_addr']
        self.subject = message_json['subject']
        self.body = message_json['body']
        self.created_at = message_json['created_at']
        self.deleted_at = message_json['deleted_at']
        self.last_attempt = message_json['last_attempt']
        self.attempts = message_json['attempts']
        self.status = message_json['status']
        self.status_code = message_json['status_code']


class Client:
    """
    mini_mailgun http client.
    """

    def __init__(self, host, port):
        """
        Args:
            host (str): The host of the mini_mailgun service.
            port (str): The port you with to connect over.
        """
        self.uri = 'http://{0}:{1}/v1/'.format(host, port)
        self.host = host
        self.port = port

    def _make_uri(self, *args):
        """
        Helper method to create the request url
        Takes n strings and joins them on / to finish
        constructing the request url.
        Args:
            *args (strs): Provide a list of strings to finish
            constructing the url.
        Returns:
            (str) A properly formatted request url.
        """
        return self.uri + '/'.join(args)

    def _check_for_errors(self, response):
        """
        Checks response for errors and raises exceptions as needed.
        Args:
            response (requests.Response) The requests response object.
        Raises:
            MessageAlreadySentError if the message has already been sent.
            ClientExceptionError on all other 4** series errors.
            ServerExceptionError on all 5** series errors.
        """
        if response.status_code >= 500:
            raise ServerExceptionError(response.status_code)
        elif response.status_code == 409:
            raise MessageAlreadySentOrFailedError(response.status_code)
        elif response.status_code >= 400 and response.status_code < 500:
            raise ClientExceptionError(response.status_code)

    def send_email(self, from_addr, to_addr, subject, body):
        """
        Send an email.
        Args:
            from_addr (str): The sender's address.
            to_addr (str): The recipiant's address.
            subject (str): The subject of the email.
            body (str): The body of the email.
        Raises:
            ClientExceptionError on a 4** series error.
            ServerExceptionError on a 5** series error.
        Returns:
            (mini_mailgun.api.client.Message)
        """
        uri = self._make_uri('email')
        data = {'from_addr': from_addr,
                'to_addr': to_addr,
                'subject': subject,
                'body': body}
        response = requests.post(uri, json=json.dumps(data),
                                 headers={'content-type': 'application/json'})
        self._check_for_errors(response)
        return Message(response.json())

    def delete_email(self, uuid):
        """
        Delete a message if it has not already been sent.
        Args:
            uuid (str): The UUID of the message.
        Raises:
            MessageAlreadySentOrFailedError if the message has
                already been sent or failed to send.
            ClientExceptionError on all other 4** series errors.
            ServerExceptionError on all 5** series errors.
        """
        uri = self._make_uri('email', uuid)
        response = requests.delete(uri)
        self._check_for_errors(response)

    def get_email(self, uuid):
        """
        Get info about an email in the system.
        Args:
            uuid (str): The UUID of the message.
        Raises:
            ClientExceptionError on all 4** series errors.
            ServerExceptionError on all 5** series errors.
        Returns:
            (mini_mailgun.api.client.Message)
        """
        uri = self._make_uri('email', uuid)
        response = requests.get(uri)
        self._check_for_errors(response)
        return Message(response.json())

    def get_emails(self, limit=1000, offset=0):
        """
        Get a list of all emails in the system. Sent or otherwise.
        Kwargs:
            limit (int): Integer to limit the number of UUID's returned
                defaults to 1000.
            offset (int): Offset to start the next request at.
                defaults to 0
        Raises:
            ClientExceptionError on all 4** series errors.
            ServerExceptionError on all 5** series errors.
        Returns:
            (list) A list of email uuids.
        """
        params = {'limit': limit, 'offset': offset}
        uri = self._make_uri('email')
        response = requests.get(uri, params=params)
        self._check_for_errors(response)
        return response.json()
