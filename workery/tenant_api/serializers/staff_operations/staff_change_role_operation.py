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


class StaffChangeRoleOperationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(
        write_only=True,
        allow_null=True,
        required=False
    )

    # Meta Information.
    class Meta:
        model = Staff
        fields = ('role',)

    def validate_role(self, value):
        """
        Include validation for valid choices.
        """
        role = int_or_none(value)
        if role is None:
            raise serializers.ValidationError("Please select a valid choice.")
        else:
            if role == FRONTLINE_GROUP_ID:
                return value

            last_modified_by = self.context['last_modified_by']
            if last_modified_by.is_management_or_executive_staff():
                return value
            raise serializers.ValidationError("You do not have permission to change the account type.")

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        #---------------------------
        # Update `SharedUser` object.
        #---------------------------
        # Attach the user to the `group` group.
        role = validated_data.get('role', None)
        if role != "NaN" and role != None:
            role = int(role)
            instance.owner.groups.set([role])
            logger.info("Updated the role.")

        #---------------------------
        # Update `Staff` object.
        #---------------------------

        # Misc
        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']

        # Save our instance.
        instance.save()
        logger.info("Updated the staff member.")

        # Return our validated data.
        return instance
