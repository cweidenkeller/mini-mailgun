"""
Common module has common utils
used in the application
"""
from datetime import datetime
from uuid import uuid4


def uuid():
    """
    Generate a UUID4 string
    Returns:
        (str) A UUID4 string
    """
    return str(uuid4())


def utc_time():
    """
    Helper method to grab UTC time.
    Returns:
        (datetime.datetime) A UTC datetime object.
    """
    return datetime.utcnow()
