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
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.models import SharedUser
# from tenant_api.serializers.associate_comment import AssociateCommentSerializer
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_api.serializers.tag import TagListCreateSerializer
from tenant_api.serializers.insurance_requirement import InsuranceRequirementListCreateSerializer
from tenant_api.serializers.vehicle_type import VehicleTypeListCreateSerializer
from tenant_foundation.models import (
    AssociateComment,
    Associate,
    Comment,
    InsuranceRequirement,
    SkillSet,
    Organization,
    VehicleType,
    HowHearAboutUsItem,
    TaskItem
)


logger = logging.getLogger(__name__)


class AssociateAddressUpdateSerializer(serializers.ModelSerializer):
    address_country = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    address_region = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
    )
    address_locality = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[]
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
        model = Associate
        fields = (
            'address_country',
            'address_locality',
            'address_region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra'
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # logger.info(validated_data)

        #---------------------------
        # Update `Associate` object.
        #---------------------------
        instance.address_country=validated_data.get('address_country', instance.address_country)
        instance.address_locality=validated_data.get('address_locality', instance.address_locality)
        instance.address_region=validated_data.get('address_region', instance.address_region)
        instance.post_office_box_number=validated_data.get('post_office_box_number', instance.post_office_box_number)
        instance.postal_code=validated_data.get('postal_code', instance.postal_code)
        instance.street_address=validated_data.get('street_address', instance.street_address)
        instance.street_address_extra=validated_data.get('street_address_extra', instance.street_address_extra)
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']
        instance.last_modified_by = self.context['last_modified_by']
        instance.save()
        logger.info("Updated the associate.")
        return instance
