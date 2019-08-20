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
from shared_foundation.constants import ASSOCIATE_GROUP_ID, FRONTLINE_GROUP_ID
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import (
    get_unique_username_from_email,
    int_or_none
)
from shared_foundation.models import SharedUser
from tenant_foundation.models import (
    Comment,
    StaffComment,
    Staff,
    HowHearAboutUsItem
)
from tenant_api.serializers.tag import TagListCreateSerializer


logger = logging.getLogger(__name__)


class StaffAddressUpdateSerializer(serializers.ModelSerializer):
    country = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address_country",
    )
    region = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[],
        source="address_region",
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

    # Meta Information.
    class Meta:
        model = Staff
        fields = (

            'country',
            'locality',
            'region',
            'post_office_box_number',
            'postal_code',
            'street_address',
            'street_address_extra',

        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            # 'comments'
            'tags',
        )
        return queryset

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        #-------------------------------------
        # Bugfix: Created `SharedUser` object.
        #-------------------------------------
        if instance.owner is None:
            owner = SharedUser.objects.filter(email=instance.email).first()
            if owner:
                instance.owner = owner
                instance.save()
                logger.info("BUGFIX: Attached existing shared user to staff.")
            else:
                instance.owner = SharedUser.objects.create(
                    first_name=instance.given_name,
                    last_name=instance.last_name,
                    email=instance.email,
                    is_active=True,
                    franchise=self.context['franchise'],
                    was_email_activated=True
                )
                instance.save()
                logger.info("BUGFIX: Created shared user and attached to staff.")

        # Update the account.
        if instance.email:
            instance.owner.email = instance.email
            instance.owner.username = get_unique_username_from_email(instance.email)
        instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
        instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)
        instance.owner.save()
        logger.info("Updated the shared user.")

        #---------------------------
        # Update `Staff` object.
        #---------------------------
        # Address
        instance.address_country=validated_data.get('address_country', None)
        instance.address_locality=validated_data.get('address_locality', None)
        instance.address_region=validated_data.get('address_region', None)
        instance.post_office_box_number=validated_data.get('post_office_box_number', None)
        instance.postal_code=validated_data.get('postal_code', None)
        instance.street_address=validated_data.get('street_address', None)
        instance.street_address_extra=validated_data.get('street_address_extra', None)

        # Misc
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']

        # Save our instance.
        instance.save()
        logger.info("Updated the staff member.")

        # Return our updated object.
        return instance
