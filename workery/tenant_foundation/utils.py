# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


UTC_ZONE = tz.gettz('UTC')
TORONTO_ZONE = tz.gettz('America/Toronto')


def bool_or_none(value):
    value = value.lower()

    if "1" in value:
        return True

    return False


def get_dt_from_toronto_timezone_ms_access_dt_string(dt_string):
    """
    Function will convert the `Microsft Access DB` datetime, formatted in
    Toronto timezone, into our timezone aware django datetime.
    """
    # Get the native timezone that the database originally used.
    toronto_timezone = pytz.timezone('America/Toronto')

    # Attempt to get our `datetime`.
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%d, %H:%M:%S %p")
        return dt.replace(tzinfo=toronto_timezone) # Make timezone aware.
    except Exception as e:
        return None


def get_utc_dt_from_toronto_dt_string(dt_string):
    # Attempt to get our `datetime`.
    try:
        dt = parser.parse(dt_string)
        aware_dt = dt.replace(tzinfo=TORONTO_ZONE) # Make timezone aware.
        aware_dt = dt.astimezone(UTC_ZONE) # Convert w/ UTC timezone.
        return aware_dt
    except Exception as e:
        return None
