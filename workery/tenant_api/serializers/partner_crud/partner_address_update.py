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


logger = logging.getLogger(__name__)


class PartnerAddressUpdateSerializer(serializers.ModelSerializer):
    country = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address_country"
    )
    region = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address_region"
    )
    locality = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address_locality"
    )
    postal_code = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    street_address = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )

    class Meta:
        model = Partner
        fields = (
            'country',
            'locality',
            'region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        #---------------------------
        # Update `Partner` object.
        #---------------------------
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.address_country=validated_data.get('address_country', None)
        instance.address_locality=validated_data.get('address_locality', None)
        instance.address_region=validated_data.get('address_region', None)
        instance.post_office_box_number=validated_data.get('post_office_box_number', None)
        instance.postal_code=validated_data.get('postal_code', None)
        instance.street_address=validated_data.get('street_address', None)
        instance.street_address_extra=validated_data.get('street_address_extra', None)
        instance.save()
        logger.info("Updated the partner.")
        return instance
