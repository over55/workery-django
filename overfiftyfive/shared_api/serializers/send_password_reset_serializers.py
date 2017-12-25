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


class SendResetPasswordEmailSerializer(serializers.Serializer):
    email_or_username = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=63,
    )
    tel_or_cell = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=16,
    )

    def validate(self, clean_data):
        """
        Check to see if the email address is unique and passwords match.
        """
        try:
            clean_data['me'] = SharedMe.objects.get(
                Q(
                    Q(user__email=clean_data['email_or_username']) |
                    Q(user__username=clean_data['email_or_username'])
                ) & Q(
                    Q(tel_num=clean_data['tel_or_cell']) |
                    Q(cell_num=clean_data['tel_or_cell'])
                )
            )
        except SharedMe.DoesNotExist:
            raise serializers.ValidationError("Email with that phone number does not exist.")
        return clean_data
