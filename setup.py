from setuptools import setup, find_packages

setup(
    name='mini_mailgun',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts':
            ['mini-mailgun = mini_mailgun.api.run:run_server']},
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask-SQLAlchemy', 'jsonschema',
                      'mysql-python', 'requests', 'redis',
                      'celery', 'gevent', 'flask', 'alembic'],
    author="Conrad Weidenkeller",
    author_email="conrad@weidenkeller.com",
    url="http://conrad.weidenkeller.com"
)
