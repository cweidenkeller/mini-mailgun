"""
mini_mailgun exception module
"""


class MiniMailgunError(Exception):
    """
    Base mini_mailgun exception.
    """
    pass


class ClientExceptionError(MiniMailgunError):
    """
    Raised when a 4** series error is sent from the api.
    """
    pass


class ServerExceptionError(MiniMailgunError):
    """
    Raised when a 5** series error is sent from the api.
    """
    pass


class MessageAlreadySentOrFailedError(MiniMailgunError):
    """
    Raised when you attempt to delete an email that has already been sent.
    Or has failed to send.
    """


class SMTPClientError(MiniMailgunError):
    """
    Raises when we the SMTP client a connection or similar error.
    """
    pass
