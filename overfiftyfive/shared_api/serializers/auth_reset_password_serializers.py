# -*- coding: utf-8 -*-
import re
from datetime import timedelta
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.core.validators import EMPTY_VALUES
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from shared_foundation.models.me import SharedMe
from shared_foundation import utils
from shared_api.custom_validation import (
    MatchingDuelFieldsValidator,
    EnhancedPasswordStrengthFieldValidator
)


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'},
        validators = [
            MatchingDuelFieldsValidator(
                another_field='password_repeat',
                message=_("Inputted passwords fields do not match.")
            ),
            EnhancedPasswordStrengthFieldValidator()
        ]
    )
    password_repeat = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=63,
        style={'input_type': 'password'}
    )
    pr_access_code = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255,
        style={'input_type': 'password'}
    )
