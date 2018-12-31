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
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    Associate,
    WorkOrder,
    ONGOING_WORK_ORDER_STATE,
    Organization,
    OngoingWorkOrder,
    OngoingWorkOrderComment,
    TaskItem
)


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


def cannot_be_zero_or_negative(value):
    if value <= 0:
        raise serializers.ValidationError('Please pick a reason from the dropdown.')
    return value


class OngoingWorkOrderCloseOperationSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=OngoingWorkOrder.objects.all(), required=True)
    reason = serializers.CharField(required=True, allow_blank=False)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'reason',
        )

    # def validate(self, data):
    #     """
    #     Override the validator to provide additional custom validation based
    #     on our custom logic.
    #
    #     1. If 'reason' == 1 then make sure 'reason_other' was inputted.
    #     """
    #     # CASE 1 - Other reason
    #     if data['reason'] == 1:
    #         reason_other = data['reason_other']
    #         if reason_other == "":
    #             raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))
    #     return data  # Return our data.

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        job = validated_data.get('job', None)
        reason = validated_data.get('reason', None)

        #------------------------------------------#
        # Create any additional optional comments. #
        #------------------------------------------#
        comment_obj = Comment.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            text=reason,
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public']
        )
        OngoingWorkOrderComment.objects.create(
            about=job,
            comment=comment_obj,
        )

        # For debugging purposes only.
        logger.info("Job comment created.")

        #-------------------------#
        # Update the ongoing job. #
        #-------------------------#
        job.state = ONGOING_WORK_ORDER_STATE.TERMINATED
        job.save()

        # For debugging purposes only.
        logger.info("Updated ongoing job.")

        #---------------------------------#
        # Close all the TaskItem objects. #
        #---------------------------------#
        for task_item in TaskItem.objects.filter(ongoing_job=job, is_closed=False):
            task_item.last_modified_by = self.context['user']
            task_item.last_modified_from = self.context['from']
            task_item.last_modified_from_is_public = self.context['from_is_public']
            task_item.is_closed = True
            task_item.closing_reason = 1  # (Other - choice.)
            task_item.closing_reason_other = 'Closed because master job was closed.'
            task_item.save()

        # Return our processed values.
        return validated_data
