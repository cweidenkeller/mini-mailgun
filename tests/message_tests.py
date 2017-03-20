import unittest

from mini_mailgun.message import Message


class MessageTestCase(unittest.TestCase):

    def test_message(self):
        m = Message('from', 'to', 'subject', 'body')
        self.assertEqual(m.from_addr, 'from')
        self.assertEqual(m.to_addr, 'to')
        self.assertEqual(m.subject, 'subject')
        self.assertEqual(m.body, 'body')
        self.assertEqual(len(m.email_message), 314)


if __name__ == '__main__':
    unittest.main()
