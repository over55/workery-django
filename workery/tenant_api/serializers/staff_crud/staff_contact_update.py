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
from shared_foundation.constants import TELEPHONE_CONTACT_POINT_TYPE_OF_ID
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


class StaffContactUpdateSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
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
    work_email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=Staff.objects.all()),
        ],
        required=False,
        source="email"
    )
    personal_email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=Staff.objects.all()),
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

    # Meta Information.
    class Meta:
        model = Staff
        fields = (
            'given_name',
            'last_name',
            'primary_phone',
            'primary_phone_type_of',
            'secondary_phone',
            'secondary_phone_type_of',
            'work_email',
            'personal_email',
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

    def validate_personal_email(self, value):
        """
        Include validation for valid choices.
        """
        if value is None or value == '':
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # # For debugging purposes only.
        # print(validated_data)

        # Get our inputs.
        work_email = validated_data.get('work_email', instance.email)
        personal_email = validated_data.get('personal_email', None)

        #-------------------------------------
        # Bugfix: Created `SharedUser` object.
        #-------------------------------------
        if instance.owner is None:
            owner = SharedUser.objects.filter(email=work_email).first()
            if owner:
                instance.owner = owner
                instance.save()
                logger.info("BUGFIX: Attached existing shared user to staff.")
            else:
                instance.owner = SharedUser.objects.create(
                    first_name=validated_data['given_name'],
                    last_name=validated_data['last_name'],
                    email=work_email,
                    is_active=True,
                    franchise=self.context['franchise'],
                    was_email_activated=True
                )
                instance.save()
                logger.info("BUGFIX: Created shared user and attached to staff.")

        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        # Update the account.
        if work_email:
            instance.owner.email = work_email
            instance.owner.username = get_unique_username_from_email(work_email)
        instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
        instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)
        instance.owner.save()
        logger.info("Updated the shared user.")

        #---------------------------
        # Update `Staff` object.
        #---------------------------
        # Person
        instance.given_name=validated_data.get('given_name', None)
        instance.last_name=validated_data.get('last_name', None)
        instance.middle_name=validated_data.get('middle_name', None)
        # Misc
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']

        # Contact Point
        instance.area_served=validated_data.get('area_served', None)
        instance.available_language=validated_data.get('available_language', None)
        instance.contact_type=validated_data.get('contact_type', None)
        instance.email=work_email
        instance.personal_email=personal_email
        # 'hours_available', #TODO: IMPLEMENT.
        instance.telephone=validated_data.get('telephone', None)
        # instance.telephone_extension=validated_data.get('telephone_extension', None)
        instance.telephone_type_of=validated_data.get('telephone_type_of', None)
        instance.other_telephone=validated_data.get('other_telephone', None)
        # instance.other_telephone_extension=validated_data.get('other_telephone_extension', None)
        instance.other_telephone_type_of=validated_data.get('other_telephone_type_of', TELEPHONE_CONTACT_POINT_TYPE_OF_ID)

        # Save our instance.
        instance.save()
        logger.info("Updated the staff member.")

        # Return our validated data.
        return instance
