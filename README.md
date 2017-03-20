# Mini Mailgun setup guide... Sorry yeah it needs a guide.

## Introduction

So, the app uses flask as the API server.. Celery for all async jobs using redis at it's broker and MySQL to store information about the messages.

## Requirements

* Virtualenvwrapper
* Redis
* MySQL

## Installation

```
cweid@top:~$ sudo apt-get install mysql-server
```
I set the default root password to *adminmorelikeradmin*.
If you want to use the example config as is please use that.
```
cweid@top:~$ sudo apt-get install redis-server
```
I did not set any password on this and am using the default port.
If you want to use the example config please use that
```
cweid@top:~$ mkvirtualenv mini_mailgun
New python executable in /home/cweid/.virtualenvs/mini_mailgun/bin/python
```
```
(mini_mailgun) cweid@top:~/code/mini-mailgun$ python setup.py develop
```
If you need to modifiy configs look at the example.conf located in mini-mailgun/etc/example.conf
and update the credentials to match your mysql and redis installs.

Next if you changed the MySQL information you will have to update the login details in the alembic.ini
Located in mini-mailgun/alembic.ini

Now we need to create the MySQL DB. This example assumes you are using the default example config credentials for MySQL.

```
(mini-mailgun) cweid@top:~$ sudo -i
root@top:~# mysql -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 17
Server version: 5.7.17-0ubuntu0.16.10.1 (Ubuntu)

Copyright (c) 2000, 2016, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> create database mini_mailgun;
Query OK, 1 row affected (0.00 sec)

mysql> exit
Bye
root@top:~#
```

Now we can bootstrap the DB with it's schema

```
(mini_mailgun) cweid@top:~/code/mini-mailgun$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0284b2835cc7, Inital schema
```

Cool we are almost done now to start up the API server and celery!

So to start the API server if you are in the mini_mailgun virtual env a small script will be exported for you.

Run it like this

```
(mini_mailgun) cweid@top:~/code/mini-mailgun$ export MINI_MAILGUN_CONFIG="/home/cweid/code/mini-mailgun/etc/example.conf";mini-mailgun
```

You should get some output like this

```
(mini_mailgun) cweid@top:~/code/mini-mailgun$ export MINI_MAILGUN_CONFIG="/home/cweid/code/mini-mailgun/etc/example.conf";mini-mailgun /home/cweid/.virtualenvs/mini_mailgun/local/lib/python2.7/site-packages/Flask_SQLAlchemy-2.2-py2.7.egg/flask_sqlalchemy/__init__.py:839: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
/home/cweid/.virtualenvs/mini_mailgun/local/lib/python2.7/site-packages/Flask_SQLAlchemy-2.2-py2.7.egg/flask_sqlalchemy/__init__.py:839: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
/home/cweid/.virtualenvs/mini_mailgun/local/lib/python2.7/site-packages/Flask_SQLAlchemy-2.2-py2.7.egg/flask_sqlalchemy/__init__.py:839: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
/home/cweid/.virtualenvs/mini_mailgun/local/lib/python2.7/site-packages/Flask_SQLAlchemy-2.2-py2.7.egg/flask_sqlalchemy/__init__.py:839: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
2017-03-18 11:09:39,194 - mini_mailgun.api.run - INFO - Starting API SERVER
```


Finally we can start up celery.

Inside the bin directory of mini-mailgun/bin there is a helper script to start celery
```
(mini_mailgun) cweid@top:~/code/mini-mailgun$ export MINI_MAILGUN_CONFIG="/home/cweid/code/mini-mailgun/etc/example.conf";bin/mini-mailgun-celery
```

You should see some output like this.

```
(mini_mailgun) cweid@top:~/code/mini-mailgun$ export MINI_MAILGUN_CONFIG="/home/cweid/code/mini-mailgun/etc/example.conf";bin/mini-mailgun-celery
/home/cweid/.virtualenvs/mini_mailgun/local/lib/python2.7/site-packages/Flask_SQLAlchemy-2.2-py2.7.egg/flask_sqlalchemy/__init__.py:839: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
/home/cweid/.virtualenvs/mini_mailgun/local/lib/python2.7/site-packages/Flask_SQLAlchemy-2.2-py2.7.egg/flask_sqlalchemy/__init__.py:839: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '

 -------------- celery@top v4.0.2 (latentcall)
---- **** -----
--- * ***  * -- Linux-4.8.11-040811-generic-x86_64-with-Ubuntu-16.10-yakkety 2017-03-18 11:13:30
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         mini_mailgun.api.app:0x7f431fd1f050
- ** ---------- .> transport:   redis://localhost:6379//
- ** ---------- .> results:     redis://localhost:6379/
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
```

## Testing it out

If you would like to run the applications unit tests run

```bash
(mini_mailgun) cweid@top:~/code/mini-mailgun$ export MINI_MAILGUN_CONFIG="/home/cweid/code/mini-mailgun/etc/example.conf";tox -etests
```

Now that you have everything up and running we can start trying out the application itslelf. By default I have it configured to usego daddys smtp servers. if you use my email address as it's origin it will allow you to send wherever. *conrad@weidenkeller.com* if not feel free to update the example.conf with whatever SMTP server you want.

I provided a simple client so it should be easy to test everything out in ipython.

```python
(mini_mailgun) cweid@top:~/code/mini-mailgun$ ipython
In [1]: from mini_mailgun.api.client import Client

In [2]: c = Client('localhost', 1234)

In [3]: res = c.send_email('conrad@weidenkeller.com', 'conrad@weidenkeller.com',
   ...: 'Hello', 'Message body')

In [5]: res.uuid
Out[5]: u'7b6a8894-31cc-49bb-9d8d-1c9e19255860'

In [6]: res.status
Out[6]: u'SENDING'

In [7]: res.body
Out[7]: u'Message body'
```

Here you can see we created a new email..
Got back some info about it. Let's see if the email sent..

```python
In [8]: res = c.get_email('7b6a8894-31cc-49bb-9d8d-1c9e19255860')

In [9]: res.status
Out[9]: u'SENT'

In [10]: res.status_code
Out[10]: 250
```

So it looks like the email was sent we can get the latest SMTP status code too.
Let's see what happens if we delete an already sent message

```python
In [11]: c.delete_email(res.uuid)
---------------------------------------------------------------------------
MessageAlreadySentOrFailedError           Traceback (most recent call last)
<ipython-input-11-63b1cb1181f2> in <module>()
----> 1 c.delete_email(res.uuid)

/home/cweid/code/mini-mailgun/mini_mailgun/api/client.py in delete_email(self, uuid)
    142         uri = self._make_uri('email', uuid)
    143         response = requests.delete(uri)
--> 144         self._check_for_errors(response)
    145
    146     def get_email(self, uuid):

/home/cweid/code/mini-mailgun/mini_mailgun/api/client.py in _check_for_errors(self, response)
     96             raise ServerExceptionError(response.status_code)
     97         elif response.status_code == 409:
---> 98             raise MessageAlreadySentOrFailedError(response.status_code)
     99         elif response.status_code >= 400 and response.status_code < 500:
    100             raise ClientExceptionError(response.status_code)

MessageAlreadySentOrFailedError: 409
```
Uh oh we can't delete a sent email!
Let's get a listing of all emails.

```python
In [12]: c.get_emails()
Out[12]: [u'7b6a8894-31cc-49bb-9d8d-1c9e19255860']

```
If we had more messages in the system it would display more UUID's.

## Conclusion

So there you have it hopefully this helps you get setup. Just some final things to note. All logs are stored in /tmp/mini-mailgun.log by default. This also stores all of the attempts we have made for messages so all status codes are retained there.
We also do some input validation on the create email call server side using JSON schema validation.

If you have any questions or have any problems feel free to hit me up at my email conrad@weidenkeller.com and I will help you out!

Thanks for looking at my code =).
