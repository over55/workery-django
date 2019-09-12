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


class StaffAccountUpdateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(
        write_only=True,
        required=True,
        error_messages={
            "invalid": _("Please pick either 'Yes' or 'No' choice.")
        }
    )

    # This field is used to assign the user to the group.
    account_type = serializers.CharField(
        write_only=True,
        allow_null=True,
        required=False
    )

    emergency_contact_telephone = PhoneNumberField(allow_null=True, required=False)
    emergency_contact_alternative_telephone = PhoneNumberField(allow_null=True, required=False)

    # Meta Information.
    class Meta:
        model = Staff
        fields = (
            'description',
            'account_type',

            'tags',
            'is_active',

            # Emergency Contact
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_telephone',
            'emergency_contact_alternative_telephone'
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

    def validate_account_type(self, value):
        """
        Include validation for valid choices.
        """
        account_type = int_or_none(value)
        if account_type is None:
            raise serializers.ValidationError("Please select a valid choice.")
        else:
            if account_type == FRONTLINE_GROUP_ID:
                return value

            last_modified_by = self.context['last_modified_by']
            if last_modified_by.is_management_or_executive_staff():
                return value
            raise serializers.ValidationError("You do not have permission to change the account type.")

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
                    email=instance.mail,
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
        if instance.email:
            instance.owner.email = instance.email
            instance.owner.username = get_unique_username_from_email(instance.email)
        instance.owner.first_name = validated_data.get('given_name', instance.owner.first_name)
        instance.owner.last_name = validated_data.get('last_name', instance.owner.last_name)
        instance.owner.is_active = validated_data.get('is_active', instance.owner.is_active)
        instance.owner.save()
        logger.info("Updated the shared user.")

        # Attach the user to the `group` group.
        account_type = validated_data.get('account_type', None)
        if account_type != "NaN" and account_type != None:
            account_type = int(account_type)
            instance.owner.groups.set([account_type])
            logger.info("Updated the group membership.")

        #---------------------------
        # Update `Staff` object.
        #---------------------------

        # Misc
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']

        # Emergency contact.
        instance.description=validated_data.get('description', None)
        instance.emergency_contact_name=validated_data.get('emergency_contact_name', None)
        instance.emergency_contact_relationship=validated_data.get('emergency_contact_relationship', None)
        instance.emergency_contact_telephone=validated_data.get('emergency_contact_telephone', None)
        instance.emergency_contact_alternative_telephone=validated_data.get('emergency_contact_alternative_telephone', None)

        # Save our instance.
        instance.save()
        logger.info("Updated the staff member.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                instance.tags.set(tags)

        # Return our validated data.
        return instance
