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


class CustomerArchiveOperationCreateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(many=False, queryset=Customer.objects.all(), required=True)
    state = serializers.CharField(required=True, allow_blank=False)
    deactivation_reason = serializers.CharField(required=True, allow_blank=False)
    deactivation_reason_other = serializers.CharField(required=True, allow_blank=True)
    comment = serializers.CharField(required=True, allow_blank=False)

    # Meta Information.
    class Meta:
        fields = (
            'customer',
            'state',
            'deactivation_reason',
            'deactivation_reason_other',
            'comment',
        )

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------------#
        # Get validated POST & context data #
        #-----------------------------------#
        customer = validated_data.get('customer')
        state = validated_data.get('state')
        deactivation_reason = validated_data.get('deactivation_reason', None)
        deactivation_reason_other = validated_data.get('deactivation_reason_other', None)
        comment_text = validated_data.get('comment')
        user = self.context['user']
        from_ip = self.context['from']
        from_is_public = self.context['from_is_public']

        #------------------------------------------#
        # Create any comments explaining decision. #
        #------------------------------------------#
        comment_obj = Comment.objects.create(
            text = comment_text,
            created_by = user,
            created_from = from_ip,
            created_from_is_public = from_is_public,
            last_modified_by = user,
            last_modified_from = from_ip,
            last_modified_from_is_public = from_is_public,
        )
        CustomerComment.objects.create(
            about=customer,
            comment=comment_obj,
        )
        # For debugging purposes only.
        logger.info("Customer comment created.")

        #-------------------------#
        # Update customer object. #
        #-------------------------#
        customer.state = state
        customer.deactivation_reason = deactivation_reason
        customer.deactivation_reason_other = deactivation_reason_other
        customer.last_modified_by = user
        customer.last_modified_from = from_ip
        customer.last_modified_from_is_public = from_is_public
        customer.save()

        # For debugging purposes only.
        logger.info("Customer updated state.")

        # Return the validated results.
        return validated_data
