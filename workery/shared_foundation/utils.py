# -*- coding: utf-8 -*-
import base64
import hashlib
import string
import re # Regex
from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.signing import Signer
from django.core.validators import RegexValidator
from django.db.models import Q
from django.urls import reverse
from django.utils import crypto
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework_jwt.settings import api_settings

from shared_foundation import constants


def reverse_with_full_domain(reverse_url_id, resolve_url_args=[]):
    url = settings.WORKERY_APP_HTTP_PROTOCOL
    url += settings.WORKERY_APP_HTTP_DOMAIN
    url += reverse(reverse_url_id, args=resolve_url_args)
    url = url.replace("None","en")
    return url


def has_permission(codename, user, group_ids):
    """
    Utility function used for looking up the codename `Permission` for the user
    group and user.
    """
    has_group_perm = Permission.objects.filter(codename=codename, group__id__in=group_ids).exists()
    has_user_perm = Permission.objects.filter(codename=codename, user=user).exists()
    return has_group_perm | has_user_perm


def get_jwt_token_and_orig_iat(authenticated_user):
    """
    Utility function which will return both an JOSN Web Token and the
    original date.
    """

    # Create our JWT payload.
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    # Generate our payload.
    payload = jwt_payload_handler(authenticated_user)

    # Include original issued at time for a brand new token,
    # to allow token refresh
    orig_iat = None
    if api_settings.JWT_ALLOW_REFRESH:
        import calendar
        orig_iat = calendar.timegm(
            datetime.utcnow().utctimetuple()
        )
        payload['orig_iat'] = orig_iat

    token = jwt_encode_handler(payload)

    # Return both the token and original date.
    return token, orig_iat


def get_end_of_date_for_this_dt(dt):   #TODO: UNIT TEST
    """Utility funciton will return last day of this month."""
    # Note: https://www.pkimber.net/howto/python/modules/dateutil.html
    return dt + relativedelta(months=+1, day=1, days=-1)


def get_first_date_for_this_dt(dt):   #TODO: UNIT TEST
    """Utility funciton will return last day of this month."""
    # Note: https://www.pkimber.net/howto/python/modules/dateutil.html
    return dt + relativedelta(day=1)


def get_date_plus_days(dt, days=0):   #TODO: UNIT TEST
    """Returns the current date plus paramter number of days."""
    return dt + timedelta(days=days)


def pretty_dt_string(dt):  #TODO: UNIT TEST
    """
    Utility function will convert the naive/aware datatime to a pretty datetime
    format which will work well for output.
    """
    if dt is None:
        return None

    try:
        dt = dt.replace(microsecond=0)
        dt = dt.replace(second=0)
        dt_string = dt.strftime("%m-%d-%Y %H:%M:%S")
    except Exception as e:
        dt_string = dt.strftime("%m-%d-%Y")
    return dt_string


def generate_hash(value=None):
    """
    TODO: UNIT TEST
    """
    # Handle null values.
    if value is None or value == '':
        value = timezone.now()
        value = value.timestamp()

    # Convert whatever data format into a string value.
    value_str = str(value)

    # Conver into UTF-8 formatted string value
    utf8_value_str = value_str.encode('utf8', 'ignore')

    # Return the hash binary data.
    byte_data = base64.urlsafe_b64encode(hashlib.sha256(utf8_value_str).digest())

    # Convert to a UTF-8 string.
    return byte_data.decode("utf-8")


def get_random_string(length=31,
                      allowed_chars='abcdefghijkmnpqrstuvwxyz'
                      'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                      '23456789'):
    """
    Random string generator simplified from Django.

    TODO: UNIT TEST
    """
    return crypto.get_random_string(length, allowed_chars)


def get_unique_username_from_email(email):
    """
    Return a hash, which will fit into django "username" field of the `User`
    object, of the email.

    TODO: UNIT TEST
    """
    email = email.lower()  # Emails should be case-insensitive unique
    hashed_email = generate_hash(email)
    return hashed_email[:30]




def int_or_none(value):
    """
    TODO: UNIT TEST
    """
    try:
        return int(value)
    except Exception as e:
        return None


def float_or_none(value):
    """
    TODO: UNIT TEST
    """
    try:
        return float(value)
    except Exception as e:
        return None
