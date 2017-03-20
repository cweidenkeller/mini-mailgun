import json
import os
import unittest

from mini_mailgun.api.app import create_app
from mini_mailgun.api.db import db
from mini_mailgun.api.client import Message
from mini_mailgun.api.models import Email


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/app.db'
        self.app.config['TESTING'] = True
        db.init_app(self.app)
        self.db = db
        self.good_body = json.dumps(
            {'from_addr': 'conrad@notkeller.com',
             'to_addr': 'conrad@weidenkeller.com',
             'subject': 'asdf',
             'body': 'foo'})
        self.bad_to_body = json.dumps({
            'from_addr': 'conrad@weidenkeller.com',
            'to_addr': 'notanemailaddress',
            'subject': 'asdf',
            'body': 'foo'})
        self.missing_to_body = json.dumps({
            'from_addr': 'conrad@weidenkeller.com',
            'subject': 'asdf',
            'body': 'foo'})
        self.long_to_body = json.dumps({
            'from_addr': 'conrad@weidenkeller.com',
            'to_addr': ''.zfill(249) + '@foo.com',
            'subject': 'asdf',
            'body': 'foo'})
        self.bad_from_body = json.dumps({
            'from_addr': 'notanemailaddress',
            'to_addr': 'conrad@weidenkeller.com',
            'subject': 'asdf',
            'body': 'foo'})
        self.missing_from_body = json.dumps({
            'to_addr': 'conrad@weidenkeller.com',
            'subject': 'asdf',
            'body': 'foo'})
        self.long_from_body = json.dumps({
            'from_addr': ''.zfill(249) + '@foo.com',
            'to_addr': 'conrad@weidenkeller.com',
            'subject': 'asdf',
            'body': 'foo'})
        self.long_subject_body = json.dumps({
            'from_addr': 'conrad@weidenkeller.com',
            'to_addr': 'conrad@weidenkeller.com',
            'subject': ''.zfill(79),
            'body': 'foo'})
        self.missing_subject_body = json.dumps({
            'from_addr': 'conrad@weidenkeller.com',
            'to_addr': 'conrad@weidenkeller.com',
            'body': 'foo'})
        self.missing_body_body = json.dumps(
            {'from_addr': 'conrad@notkeller.com',
             'to_addr': 'conrad@weidenkeller.com',
             'subject': 'asdf'})
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        os.unlink('/tmp/app.db')

    def _get_message(self, data):
        return Message(json.loads(data))

    def test_get_emails(self):
        rv = self.client.get('/v1/email')
        self.assertEqual(200, rv.status_code)
        self.assertEqual('[]', rv.data)
        rv = self.client.post('/v1/email', data=self.good_body,
                              content_type='application/json')
        self.assertEqual(201, rv.status_code)
        message = self._get_message(rv.data)
        rv = self.client.get('/v1/email')
        self.assertEqual(200, rv.status_code)
        self.assertEqual(rv.data, '["' + message.uuid + '"]')

    def test_send_email(self):
        rv = self.client.post('/v1/email', data=self.good_body,
                              content_type='application/json')
        self.assertEqual(201, rv.status_code)
        message = self._get_message(rv.data)
        self.assertEqual(message.from_addr, 'conrad@notkeller.com')
        self.assertEqual(message.to_addr, 'conrad@weidenkeller.com')
        self.assertEqual(message.subject, 'asdf')
        self.assertEqual(message.body, 'foo')
        self.assertEqual(message.status, 'SENDING')
        self.assertEqual(message.status_code, None)
        self.assertEqual(message.deleted_at, 'None')
        self.assertEqual(message.last_attempt, 'None')
        self.assertEqual(message.attempts, 0)
        self.assertIsNotNone(message.created_at)

    def test_send_email_bad_to(self):
        rv = self.client.post('/v1/email', data=self.bad_to_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_missing_to(self):
        rv = self.client.post('/v1/email', data=self.missing_to_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_long_to(self):
        rv = self.client.post('/v1/email', data=self.long_to_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_bad_from(self):
        rv = self.client.post('/v1/email', data=self.bad_from_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_missing_from(self):
        rv = self.client.post('/v1/email', data=self.missing_from_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_long_from(self):
        rv = self.client.post('/v1/email', data=self.long_from_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_long_subject(self):
        rv = self.client.post('/v1/email', data=self.long_subject_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_missing_subject(self):
        rv = self.client.post('/v1/email', data=self.missing_subject_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_send_email_missing_body(self):
        rv = self.client.post('/v1/email', data=self.missing_body_body,
                              content_type='application/json')
        self.assertEqual(400, rv.status_code)

    def test_get_email(self):
        rv = self.client.post('/v1/email', data=self.good_body,
                              content_type='application/json')
        self.assertEqual(201, rv.status_code)
        message = self._get_message(rv.data)
        rv = self.client.get('/v1/email/' + message.uuid)
        message = self._get_message(rv.data)
        self.assertEqual(200, rv.status_code)
        self.assertEqual(message.from_addr, 'conrad@notkeller.com')
        self.assertEqual(message.to_addr, 'conrad@weidenkeller.com')
        self.assertEqual(message.subject, 'asdf')
        self.assertEqual(message.body, 'foo')
        self.assertEqual(message.status, 'SENDING')
        self.assertEqual(message.status_code, None)
        self.assertEqual(message.deleted_at, 'None')
        self.assertEqual(message.last_attempt, 'None')
        self.assertEqual(message.attempts, 0)
        self.assertIsNotNone(message.created_at)

    def test_get_email_not_found(self):
        rv = self.client.get('/v1/email/404')
        self.assertEqual(404, rv.status_code)

    def test_delete_email(self):
        rv = self.client.post('/v1/email', data=self.good_body,
                              content_type='application/json')
        self.assertEqual(201, rv.status_code)
        message = self._get_message(rv.data)
        rv = self.client.delete('/v1/email/' + message.uuid)
        self.assertEqual(200, rv.status_code)

    def test_delete_email_not_found(self):
        rv = self.client.delete('/v1/email/404')
        self.assertEqual(404, rv.status_code)

    def test_get_email_already_sent(self):
        rv = self.client.post('/v1/email', data=self.good_body,
                              content_type='application/json')
        self.assertEqual(201, rv.status_code)
        message = self._get_message(rv.data)
        with self.app.app_context():
            email = Email.query.filter_by(uuid=message.uuid).first()
            email.status = 'SENT'
            self.db.session.add(email)
            self.db.session.commit()
        rv = self.client.delete('/v1/email/' + message.uuid)
        self.assertEqual(409, rv.status_code)

    def test_get_email_already_failed(self):
        rv = self.client.post('/v1/email', data=self.good_body,
                              content_type='application/json')
        self.assertEqual(201, rv.status_code)
        message = self._get_message(rv.data)
        with self.app.app_context():
            email = Email.query.filter_by(uuid=message.uuid).first()
            email.status = 'FAILED'
            self.db.session.add(email)
            self.db.session.commit()
        rv = self.client.delete('/v1/email/' + message.uuid)
        self.assertEqual(409, rv.status_code)


if __name__ == '__main__':
    unittest.main()
