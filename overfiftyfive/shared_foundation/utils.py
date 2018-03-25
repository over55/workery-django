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


"""
class StringArray(object):
    arr = []

def unique_string_arr_append(string_arr, new_string_value):
    # Assume that the item does not exist.
    does_not_exist = True
    # Prove that this new string does not exist in the array.
    for string_value in string_arr:
        if new_string_value == string_value:
            does_not_exist = False

    if does_not_exist:
        string_arr.append(new_string_value)

    return string_arr
"""
