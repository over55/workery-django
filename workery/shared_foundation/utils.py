# -*- coding: utf-8 -*-
import base64
import hashlib
import string
import re # Regex
from datetime import date, timedelta, datetime, time
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
    url = settings.O55_APP_HTTP_PROTOCOL
    url += settings.O55_APP_HTTP_DOMAIN
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
