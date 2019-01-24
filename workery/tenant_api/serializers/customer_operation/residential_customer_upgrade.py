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
from shared_foundation.utils import int_or_none
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    Customer,
    CustomerComment,
    ActivitySheetItem,
    Associate,
    WorkOrder,
    WORK_ORDER_STATE,
    WorkOrderComment,
    Organization,
    TaskItem
)


logger = logging.getLogger(__name__)


class ResidentialCustomerUpgradeOperationCreateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(many=False, queryset=Customer.objects.all(), required=True)
    #
    # Fields used for mapping to organizations.
    #

    organization_name = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        allow_null=False,
        max_length=63,
        # validators=[
        #     UniqueValidator(
        #         queryset=Organization.objects.all(),
        #     )
        # ],
    )
    organization_type_of = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        max_length=63,
    )
    organization_address_country = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=True,
        max_length=127,
    )
    organization_address_locality = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=True,
        max_length=127,
    )
    organization_address_region = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=True,
        max_length=127,
    )
    organization_post_office_box_number = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )
    organization_postal_code = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=127,
    )
    organization_street_address = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=True,
        max_length=255,
    )
    organization_street_address_extra = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=255,
    )

    # Meta Information.
    class Meta:
        fields = (
            'customer',
            'organization_name',
            'organization_type_of',
            'organization_address_country',
            'organization_address_locality',
            'organization_address_region',
            'organization_post_office_box_number',
            'organization_postal_code',
            'organization_street_address',
            'organization_street_address_extra',
        )

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        customer = validated_data.get('customer', None)
        logger.info("Detected commercial customer...")

        organization_name = validated_data.get('organization_name', None)
        organization_type_of = int_or_none(validated_data.get('organization_type_of', None))
        organization_address_country = validated_data.get('organization_address_country', None)
        organization_address_locality = validated_data.get('organization_address_locality', None)
        organization_address_region = validated_data.get('organization_address_region', None)
        organization_post_office_box_number = validated_data.get('organization_post_office_box_number', None)
        organization_postal_code = validated_data.get('organization_postal_code', None)
        organization_street_address = validated_data.get('organization_street_address', None)
        organization_street_address_extra = validated_data.get('organization_street_address_extra', None)

        organization, created = Organization.objects.update_or_create(
            name=organization_name,
            type_of=organization_type_of,
            defaults={
                'type_of': organization_type_of,
                'name': organization_name,
                'address_country': organization_address_country,
                'address_locality': organization_address_locality,
                'address_region': organization_address_region,
                'post_office_box_number': organization_post_office_box_number,
                'postal_code': organization_postal_code,
                'street_address': organization_street_address,
                'street_address_extra': organization_street_address_extra,
            }
        )
        logger.info("Created organization.")
        if created:
            logger.info("Created organization.")
            organization.owner = customer.owner
            organization.save()

        customer.organization = organization
        customer.type_of = COMMERCIAL_CUSTOMER_TYPE_OF_ID
        customer.save()
        logger.info("Attached created organization to customer.")
        # Return the validated results.
        return validated_data
