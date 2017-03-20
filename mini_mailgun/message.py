"""
Python message creation module.
"""
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


class Message:
    """
    Simple class to construct and email message.
    """

    def __init__(self, from_addr, to_addr, subject, body):
        """
        Contructor that builds the email message.
        Args:
            from_addr (str): The sender's email address.
            to_addr (str): The recipiant's email address.
            subject (str): The subject of the email.
            body (str): The message body.
        Kwargs:
            None
        Raises:
            None
        Returns:
            None
        """
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.subject = subject
        self.body = body
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        self.email_message = msg.as_string()
