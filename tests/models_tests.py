import unittest

from mini_mailgun.api.models import Email


class EmailTestCase(unittest.TestCase):

    def test_email(self):
        e = Email('from', 'to', 'subject', 'body')
        self.assertEqual(e.from_addr, 'from')
        self.assertEqual(e.to_addr, 'to')
        self.assertEqual(e.subject, 'subject')
        self.assertEqual(e.body, 'body')
        m = e.to_msg()
        self.assertEqual(m.from_addr, 'from')
        self.assertEqual(m.to_addr, 'to')
        self.assertEqual(m.subject, 'subject')
        self.assertEqual(m.body, 'body')
        self.assertEqual(len(m.email_message), 314)


if __name__ == '__main__':
    unittest.main()
