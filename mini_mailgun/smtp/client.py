"""
SMTP client used to send email messages
"""
from smtplib import SMTP, SMTPException

from mini_mailgun.exceptions import SMTPClientError


class MiniMailgunSMTP(SMTP):
    """
    Subclass of pythons SMTP client.
    With it's current implementation it did not return
    2** series SMTP status codes.
    """

    def __init__(self, host, port):
        """
        Construct a MiniMailgunSMTP Object
        Args:
            host (str): SMTP host you with to connect to.
            port (int): The port on the SMTP host
                        you would like to connect over.
        """
        SMTP.__init__(self, host, port)

    def sendmail_get_status(self, from_addr, to_addr, msg):
        """
        Modified version of the SMTP sendmail method.
        It no longer supports multiple to_addrs.
        Args:
            from_addr (str): The sender's email address.
            to_addr (str): The recipiant's email address.
            msg (str): The email message.
        Returns:
            (dict): A dictionary of the last SMTP status code
                and the servers last status message.
        """
        self.ehlo_or_helo_if_needed()
        try:
            (code, resp) = self.mail(from_addr)
            if code != 250:
                return {'code': code, 'message': resp}
            (code, resp) = self.rcpt(to_addr)
            if (code != 250) and (code != 251):
                return {'code': code, 'message': resp}
            (code, resp) = self.data(msg)
            return {'code': code, 'message': resp}
        finally:
            self.rset()


class Client():
    """
    A reusable SMTP client.
    """

    def __init__(self, host, port, username=None,
                 password=None, use_tls=False):
        """
        Contructor for the SMTP client.
        Args:
            host (str): The SMTP host you wish to connect to.
            port (int): The port you wish to connect over.
        Kwargs:
            username (str): Username to be used for SMTP auth.
                            Defaults to None.
            password (str): The password of the user using SMTP auth.
                            Defaults to None.
            use_tls (bool): Enable to use tls connections. Defaults to False.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.connect()

    def connect(self):
        """
        Connect or reconnect to the SMTP host.
        Args:
            None
        Kwargs:
            None
        Raises:
            mini_mailgun.exceptions.SMTPClientError
        """
        try:
            self._smtp_connection = MiniMailgunSMTP(self.host, self.port)
            self._smtp_connection.ehlo_or_helo_if_needed()
            if self.use_tls:
                self._smtp_connection.starttls()
            if self.username and self.password:
                self._smtp_connection.login(self.username, self.password)
        except SMTPException as e:
            self.smtp_connection.quit()
            raise SMTPClientError(str(e))

    def quit(self):
        """
        Close an SMTP connection.
        """
        self._smtp_connection.quit()

    def send_message(self, from_addr, to_addr, message):
        """
        Send an email message.
        Args:
            from_addr (str): The sender's address.
            to_addr (str): The recipiant's address.
            message (str): A well formed email message.
        Returns:
            (dict): A dict containing status code
                    and last message from the server.
        """
        return self._smtp_connection.sendmail_get_status(from_addr,
                                                         to_addr,
                                                         message)
