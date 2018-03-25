# -*- coding: utf-8 -*-
import re
from datetime import timedelta
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.core.validators import EMPTY_VALUES
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from starterkit.drf.validation import (
    MatchingDuelFieldsValidator,
    EnhancedPasswordStrengthFieldValidator
)
from shared_foundation.models import SharedUser
from shared_foundation import utils


class SendResetPasswordEmailSerializer(serializers.Serializer):
    email_or_username = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=63,
    )

    def validate(self, clean_data):
        """
        Check to see if the email address is unique and passwords match.
        """
        try:
            clean_data['me'] = SharedUser.objects.get(email__iexact=clean_data['email_or_username'])
        except SharedUser.DoesNotExist:
            raise serializers.ValidationError("Email does not exist.")
        return clean_data
