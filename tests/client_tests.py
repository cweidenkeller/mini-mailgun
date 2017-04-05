import unittest

import mock

from mini_mailgun.api.client import Client
from mini_mailgun.exceptions import ClientExceptionError, ServerExceptionError
from mini_mailgun.exceptions import MessageAlreadySentOrFailedError


class ClientTestCase(unittest.TestCase):

    def setUp(self):
        self.c = Client('asdf', 80)
        self.message = {'uuid': 'uuid',
                        'from_addr': 'from_addr',
                        'to_addr': 'to_addr',
                        'subject': 'subject',
                        'body': 'body',
                        'created_at': 'created_at',
                        'deleted_at': 'deleted_at',
                        'last_attempt': 'last_attempt',
                        'attempts': 'attempts',
                        'status': 'status',
                        'status_code': 'status_code'}

    def tearDown(self):
        pass

    @mock.patch('requests.get')
    def test_get_emails(self, mock_get):
        m_response = mock.Mock()
        m_response.status_code = 200
        m_response.json = mock.Mock(return_value=['asdf'])
        mock_get.return_value = m_response
        res = self.c.get_emails()
        self.assertEquals('asdf', res[0])

    @mock.patch('requests.get')
    def test_get_emails_400(self, mock_get):
        m_response = mock.Mock()
        m_response.status_code = 400
        mock_get.return_value = m_response
        with self.assertRaises(ClientExceptionError):
            self.c.get_emails()

    @mock.patch('requests.get')
    def test_get_emails_500(self, mock_get):
        m_response = mock.Mock()
        m_response.status_code = 500
        mock_get.return_value = m_response
        with self.assertRaises(ServerExceptionError):
            self.c.get_emails()

    @mock.patch('requests.get')
    def test_get_email(self, mock_get):
        m_response = mock.Mock()
        m_response.status_code = 200
        m_response.json = mock.Mock(return_value=self.message)
        mock_get.return_value = m_response
        res = self.c.get_email('from')
        self.assertEquals(res.uuid, 'uuid')
        self.assertEquals(res.from_addr, 'from_addr')
        self.assertEquals(res.to_addr, 'to_addr')
        self.assertEquals(res.subject, 'subject')
        self.assertEquals(res.body, 'body')
        self.assertEquals(res.created_at, 'created_at')
        self.assertEquals(res.deleted_at, 'deleted_at')
        self.assertEquals(res.last_attempt, 'last_attempt')
        self.assertEquals(res.attempts, 'attempts')
        self.assertEquals(res.status, 'status')
        self.assertEquals(res.status_code, 'status_code')

    @mock.patch('requests.get')
    def test_get_email_400(self, mock_get):
        m_response = mock.Mock()
        m_response.status_code = 400
        mock_get.return_value = m_response
        with self.assertRaises(ClientExceptionError):
            self.c.get_email('from')

    @mock.patch('requests.get')
    def test_get_email_500(self, mock_get):
        m_response = mock.Mock()
        m_response.status_code = 500
        mock_get.return_value = m_response
        with self.assertRaises(ServerExceptionError):
            self.c.get_email('from')

    @mock.patch('requests.post')
    def test_send_email(self, mock_post):
        m_response = mock.Mock()
        m_response.status_code = 200
        m_response.json = mock.Mock(return_value=self.message)
        mock_post.return_value = m_response
        res = self.c.send_email('from', 'to', 'sub', 'body')
        self.assertEquals(res.uuid, 'uuid')
        self.assertEquals(res.from_addr, 'from_addr')
        self.assertEquals(res.to_addr, 'to_addr')
        self.assertEquals(res.subject, 'subject')
        self.assertEquals(res.body, 'body')
        self.assertEquals(res.created_at, 'created_at')
        self.assertEquals(res.deleted_at, 'deleted_at')
        self.assertEquals(res.last_attempt, 'last_attempt')
        self.assertEquals(res.attempts, 'attempts')
        self.assertEquals(res.status, 'status')
        self.assertEquals(res.status_code, 'status_code')

    @mock.patch('requests.post')
    def test_send_email_400(self, mock_post):
        m_response = mock.Mock()
        m_response.status_code = 400
        mock_post.return_value = m_response
        with self.assertRaises(ClientExceptionError):
            self.c.send_email('from', 'to', 'sub', 'body')

    @mock.patch('requests.post')
    def test_send_email_500(self, mock_post):
        m_response = mock.Mock()
        m_response.status_code = 500
        mock_post.return_value = m_response
        with self.assertRaises(ServerExceptionError):
            self.c.send_email('from', 'to', 'sub', 'body')

    @mock.patch('requests.delete')
    def test_delete_email(self, mock_delete):
        m_response = mock.Mock()
        m_response.status_code = 200
        m_response.json = mock.Mock(return_value=self.message)
        mock_delete.return_value = m_response
        self.c.delete_email('from')
        mock_delete.assert_called_with('http://asdf:80/v1/email/from')

    @mock.patch('requests.delete')
    def test_delete_email_400(self, mock_delete):
        m_response = mock.Mock()
        m_response.status_code = 400
        mock_delete.return_value = m_response
        with self.assertRaises(ClientExceptionError):
            self.c.delete_email('from')

    @mock.patch('requests.delete')
    def test_delete_email_409(self, mock_delete):
        m_response = mock.Mock()
        m_response.status_code = 409
        mock_delete.return_value = m_response
        with self.assertRaises(MessageAlreadySentOrFailedError):
            self.c.delete_email('from')

    @mock.patch('requests.delete')
    def test_delete_email_500(self, mock_delete):
        m_response = mock.Mock()
        m_response.status_code = 500
        mock_delete.return_value = m_response
        with self.assertRaises(ServerExceptionError):
            self.c.delete_email('from')


if __name__ == '__main__':
    unittest.main()
