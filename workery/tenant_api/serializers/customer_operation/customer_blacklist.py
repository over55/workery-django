# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from starterkit.drf.validation import (
    MatchingDuelFieldsValidator,
    EnhancedPasswordStrengthFieldValidator
)
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email
)
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
from shared_api.custom_fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
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


class CustomerBlacklistOperationCreateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(many=False, queryset=Customer.objects.all(), required=True)
    is_blacklisted = serializers.BooleanField(required=True,)
    reason = serializers.CharField(required=True, allow_blank=False)

    # Meta Information.
    class Meta:
        fields = (
            'customer',
            'is_blacklisted',
            'reason',
        )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        customer = validated_data.get('customer', None)
        is_blacklisted = validated_data.get('is_blacklisted', True)
        reason = validated_data.get('reason', None)

        #------------------------------------------#
        # Create any comments explaining decision. #
        #------------------------------------------#
        comment_obj = Comment.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            text=reason,
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public']
        )
        CustomerComment.objects.create(
            about=customer,
            comment=comment_obj,
        )

        #-------------------------#
        # Update customer object. #
        #-------------------------#
        customer.is_blacklisted = is_blacklisted
        customer.last_modified_by = self.context['user']
        customer.last_modified_from = self.context['from']
        customer.last_modified_from_is_public = self.context['from_is_public']
        customer.save()

        # For debugging purposes only.
        logger.info("Customer comment created.")

        # Return the validated results.
        return validated_data
