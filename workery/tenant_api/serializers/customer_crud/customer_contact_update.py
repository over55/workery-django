# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import get_unique_username_from_email
# from tenant_api.serializers.customer_comment import CustomerCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    CustomerComment,
    Customer,
    Organization,
    HowHearAboutUsItem
)


logger = logging.getLogger(__name__)


class CustomerContactUpdateSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[
            UniqueValidator(queryset=Customer.objects.all()),
        ],
    )
    organization_type_of = serializers.IntegerField(
        required=False,
    )
    given_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    last_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    # We are overriding the `email` field to include unique email validation.
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=Customer.objects.all()),
        ],
        required=False
    )

    # Custom formatting of our telephone fields.
    primary_phone = PhoneNumberField(allow_null=False, required=True, source="telephone")
    primary_phone_type_of = serializers.IntegerField(
        required=True,
        validators=[],
        source="telephone_type_of"
    )
    secondary_phone = PhoneNumberField(allow_null=True, required=False, source="other_telephone")
    secondary_phone_type_of = serializers.IntegerField(
        required=False,
        validators=[],
        source="other_telephone_type_of"
    )

    class Meta:
        model = Customer
        fields = (
            'organization_name',
            'organization_type_of',
            'given_name',
            'last_name',
            'email',
            'primary_phone',
            'primary_phone_type_of',
            'secondary_phone',
            'secondary_phone_type_of',
            'is_ok_to_email',
            'is_ok_to_text',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            'tags',
            'comments',
            'organization'
        )
        return queryset

    def get_organization_name(self, data):
        if data.get('type_of', None) == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
            organization_name = data.get('organization_name', None)
            if organization_name is None:
                raise serializers.ValidationError(_("Please provide the organization name."))
        return data

    def get_organization_type_of(self, data):
        if data.get('type_of', None) == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
            organization_type_of = data.get('organization_type_of', None)
            if organization_type_of is None:
                raise serializers.ValidationError(_("Please provide the organization type of."))
        return data

    def validate(self, data):
        """
        Override the validator to provide additional custom validation based
        on our custom logic.

        1. If 'type_of' == Commercial then make sure 'email' was inputted.
        """
        # CASE 1 - Other reason
        if data.get('type_of', None) == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
            email = data.get('email', None)
            if email is None:
                raise serializers.ValidationError(_("Please provide an email if client is commercial."))

        # Return our data.
        return data

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # Get our inputs.
        email = validated_data.get('email', instance.email)

        #-----------------------------------------------------------
        # Bugfix: Created `SharedUser` object if not created before.
        #-----------------------------------------------------------
        if instance.owner is None and email:
            owner = SharedUser.objects.filter(email=email).first()
            if owner:
                instance.owner = owner
                instance.save()
                logger.info("BUGFIX: Attached existing shared user to staff.")
            else:
                instance.owner = SharedUser.objects.create(
                    first_name=validated_data['given_name'],
                    last_name=validated_data['last_name'],
                    email=email,
                    is_active=True,
                    franchise=self.context['franchise'],
                    was_email_activated=True
                )
                instance.save()
                logger.info("BUGFIX: Created shared user and attached to staff.")

        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        if instance.owner:
            # Update details.
            instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
            instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)

            if email:
                instance.owner.email = email
                instance.owner.username = get_unique_username_from_email(email)

            # Update the password.
            password = validated_data.get('password', None)
            instance.owner.set_password(password)

            # Save the model to the database.
            instance.owner.save()
            logger.info("Updated shared user.")

        #---------------------------
        # Update `Customer` object.
        #---------------------------
        instance.given_name = validated_data.get('given_name', instance.given_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.last_modified_by = self.context['last_modified_by']
        instance.is_ok_to_email = validated_data.get('is_ok_to_email', instance.is_ok_to_email)
        instance.is_ok_to_text = validated_data.get('is_ok_to_text', instance.is_ok_to_text)

        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.organization_name=validated_data.get('organization_name', instance.organization_name)
        instance.organization_type_of=validated_data.get('organization_type_of', instance.organization_type_of)

        instance.email = validated_data.get('email', instance.contact_type)
        instance.telephone=validated_data.get('telephone', None)
        instance.telephone_extension=validated_data.get('telephone_extension', None)
        instance.telephone_type_of=validated_data.get('telephone_type_of', None)
        instance.other_telephone=validated_data.get('other_telephone', None)
        instance.other_telephone_extension=validated_data.get('other_telephone_extension', None)
        instance.other_telephone_type_of=validated_data.get('other_telephone_type_of', None)

        instance.save()
        logger.info("Updated the customer.")
        return instance
