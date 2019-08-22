# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
# from tenant_api.serializers.partner_comment import PartnerCommentSerializer
from tenant_foundation.models import (
    PartnerComment,
    Partner,
    Comment,
    SkillSet,
    Organization,
    HowHearAboutUsItem
)
from tenant_foundation.constants import *


logger = logging.getLogger(__name__)


class PartnerContactUpdateSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
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
        validators=[UniqueValidator(queryset=Partner.objects.all())],
        required=True,
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
        model = Partner
        fields = (
            'organization_name',
            'given_name',
            'last_name',
            'primary_phone',
            'primary_phone_type_of',
            'secondary_phone',
            'secondary_phone_type_of',
            'email',
            'is_ok_to_email',
            'is_ok_to_text',
        )
        extra_kwargs = {
            "is_ok_to_email": {
                "error_messages": {
                    "invalid": _("Please pick either 'Yes' or 'No' choice.")
                }
            },
            "is_ok_to_text": {
                "error_messages": {
                    "invalid": _("Please pick either 'Yes' or 'No' choice.")
                }
            },
        }

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        # Get our inputs.
        email = validated_data.get('email', instance.email)

        # Update telephone numbers.
        telephone = validated_data.get('telephone', instance.telephone)
        if telephone is not None:
            validated_data['telephone'] = phonenumbers.parse(telephone, "CA")
        other_telephone = validated_data.get('other_telephone', instance.other_telephone)
        if other_telephone is not None:
            validated_data['other_telephone'] = phonenumbers.parse(other_telephone, "CA")

        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        instance.owner, created = SharedUser.objects.update_or_create(
            email=email,
            defaults={
                'email': email,
                'first_name': validated_data.get('given_name', instance.given_name),
                'last_name': validated_data.get('last_name', instance.last_name),
                'is_active': True
            }
        )
        logger.info("Updated shared user.")

        #---------------------------
        # Update `Partner` object.
        #---------------------------
        instance.email = email
        instance.organization_name = validated_data.get('organization_name', None)
        instance.organization_type_of = validated_data.get('organization_type_of', UNKNOWN_ORGANIZATION_TYPE_OF_ID)
        instance.given_name=validated_data.get('given_name', instance.given_name)
        instance.last_name=validated_data.get('last_name', instance.last_name)
        instance.middle_name=validated_data.get('middle_name', instance.middle_name)
        instance.is_ok_to_email=validated_data.get('is_ok_to_email', None)
        instance.is_ok_to_text=validated_data.get('is_ok_to_text', None)
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.telephone=validated_data.get('telephone', None)
        instance.telephone_extension=validated_data.get('telephone_extension', None)
        instance.telephone_type_of=validated_data.get('telephone_type_of', TELEPHONE_CONTACT_POINT_TYPE_OF_ID)
        instance.other_telephone=validated_data.get('other_telephone', None)
        instance.other_telephone_extension=validated_data.get('other_telephone_extension', None)
        instance.other_telephone_type_of=validated_data.get('other_telephone_type_of', TELEPHONE_CONTACT_POINT_TYPE_OF_ID)
        instance.save()
        logger.info("Updated the partner.")
        return instance
