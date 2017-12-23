# -*- coding: utf-8 -*-
import base64
import hashlib
import string
import re # Regex
from datetime import date, timedelta, datetime, time
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.signing import Signer
from django.core.validators import RegexValidator
from django.db.models import Q
from django.utils import crypto
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants


"""
Lambda function takes the "range" function, which is default for python, and
creates a function which is inclusive.
"""
inc_range = lambda start, end: range(start, end+1)


def get_random_string(length=31,
                      allowed_chars='abcdefghijkmnpqrstuvwxyz'
                      'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                      '23456789'):
    """
    Random string generator simplified from Django.
    """
    return crypto.get_random_string(length, allowed_chars)


def generate_hash(value=timezone.now()):
    # Convert whatever data format into a string value.
    value_str = str(value)

    # Conver into UTF-8 formatted string value
    utf8_value_str = value_str.encode('utf8', 'ignore')

    # Return the hash
    return base64.urlsafe_b64encode(hashlib.sha256(utf8_value_str).digest())


def get_unique_username_from_email(email):
    """
    Return a hash, which will fit into django "username" field of the `User`
    object, of the email.
    """
    email = email.lower()  # Emails should be case-insensitive unique
    hashed_email = generate_hash(email)
    return hashed_email[:30]


def int_or_none(value):
    try:
        return int(value)
    except Exception as e:
        return None


def float_or_none(value):
    try:
        return float(value)
    except Exception as e:
        return None
