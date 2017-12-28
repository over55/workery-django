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
from rest_framework.validators import UniqueValidator
from starterkit.drf.validation import (
    MatchingDuelFieldsValidator,
    EnhancedPasswordStrengthFieldValidator,
    OnlyTrueBooleanFieldValidator
)
from starterkit.utils import get_unique_username_from_email
from shared_foundation.models import SharedMe


class RegisterCustomerSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=100)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=100)
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=63,
        validators = [
            UniqueValidator( # See via http://www.django-rest-framework.org/api-guide/validators/#uniquevalidator
                queryset=User.objects.all(),
                message=_('This field must be unique.')
            ),
        ]
    )
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
    has_signed_tos = serializers.BooleanField(
        required=True,
        validators = [
            OnlyTrueBooleanFieldValidator(
                message=_("You must agree to Over 55 terms of service before registering.")
            )
        ]
    )
    schema_name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=31
    )
    telephone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=16,
        validators = []
    )
    telephone_extension = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=16,
        validators = []
    )
    mobile = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=16,
        validators = []
    )
    address_country = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=127,
        validators = []
    )
    address_locality = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=127,
        validators = []
    )
    address_region = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=127,
        validators = []
    )
    post_office_box_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=127,
        validators = []
    )
    postal_code = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=127,
        validators = []
    )
    street_address = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=127,
        validators = []
    )
    street_address_extra = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=127,
        validators = []
    )

    def validate(self, clean_data):
        telephone = clean_data['telephone']
        mobile = clean_data['mobile']

        if telephone is '' and mobile is '':
            raise serializers.ValidationError(_("Please fill either mobile or telephone number."))

        return clean_data

    def create(self, cleaned_data):
        # Create our user.
        email = cleaned_data['email']
        user = User.objects.create(
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            email=email,
            username=get_unique_username_from_email(email),
            is_active=True,
            is_staff=False,
            is_superuser=False
        )

        # Set the users password.
        user.set_password(cleaned_data['password'])
        user.is_active = True
        user.save()
        cleaned_data['user'] = user

        me = SharedMe.objects.create(
            user=user,
            telephone=cleaned_data['telephone'],
            telephone_extension=cleaned_data['telephone_extension'],
            mobile=cleaned_data['mobile'],
            address_country=cleaned_data['address_country'],
            address_locality=cleaned_data['address_locality'],
            address_region=cleaned_data['address_region'],
            post_office_box_number=cleaned_data['post_office_box_number'],
            postal_code=cleaned_data['postal_code'],
            street_address=cleaned_data['street_address'],
            street_address_extra=cleaned_data['street_address_extra'],
        )
        cleaned_data['me'] = me

        # Return our validated data.
        return cleaned_data
