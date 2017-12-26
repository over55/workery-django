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
from django.urls import reverse
from django.utils import crypto
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants


def reverse_with_full_domain(reverse_url_id, resolve_url_args=[]):
    url = settings.O55_APP_HTTP_PROTOCOL
    url += settings.O55_APP_HTTP_DOMAIN
    url += reverse(reverse_url_id, args=resolve_url_args)
    url = url.replace("None","en")
    return url
