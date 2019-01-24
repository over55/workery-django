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
    ActivitySheetItem,
    Associate,
    WorkOrder,
    WORK_ORDER_STATE,
    WorkOrderComment,
    Organization,
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


def cannot_be_negative(value):
    if value < 0:
        raise serializers.ValidationError('Please enter an amount which is not negative!')
    return value


class CompletedWorkOrderCancelOperationSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), required=True)
    reason = serializers.IntegerField(required=False, validators=[cannot_be_zero_or_negative,])
    reason_other = serializers.CharField(required=False, allow_blank=True)
    additional_comment = serializers.CharField(required=False, allow_blank=True)
    latest_pending_task = serializers.ReadOnlyField()

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'reason',
            'reason_other',
            'additional_comment',
            'latest_pending_task'
        )

    def validate(self, data):
        """
        Override the validator to provide additional custom validation based
        on our custom logic.

        1. If 'reason' == 1 then make sure 'reason_other' was inputted.
        """
        if data['reason'] == 1:
            reason_other = data['reason_other']
            if reason_other == "":
                raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))

        # Return our data.
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        job = validated_data.get('job', None)
        reason = validated_data.get('reason', None)
        reason_other = validated_data.get('reason_other', None)
        additional_comment_text = validated_data.get('additional_comment', None)

        #---------------------------------------------------#
        # Create any additional comment for `reason_other`. #
        #---------------------------------------------------#
        if reason_other:
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                text=reason_other,
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public']
            )
            WorkOrderComment.objects.create(
                about=job,
                comment=comment_obj,
            )

            # For debugging purposes only.
            logger.info("Job comment created.")

        #------------------------------------------#
        # Create any additional optional comments. #
        #------------------------------------------#
        if additional_comment_text:
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                text=additional_comment_text,
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public']
            )
            WorkOrderComment.objects.create(
                about=job,
                comment=comment_obj,
            )

            # For debugging purposes only.
            logger.info("Job comment created.")

        #----------------------------------------#
        # Lookup our Task(s) and close them all. #
        #----------------------------------------#
        for task_item in TaskItem.objects.filter(job=job,is_closed=False):
            logger.info("Found task # #%(id)s ." % {
                'id': str(task_item.id)
            })
            task_item.reason = reason
            task_item.reason_other = reason_other
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.save()
            logger.info("Task #%(id)s was closed." % {
                'id': str(task_item.id)
            })

        # ------------------------
        # --- JOB IS CANCELLED ---
        # ------------------------
        job.closing_reason = reason
        job.closing_reason_other = reason_other
        job.last_modified_by = self.context['user']
        job.state = WORK_ORDER_STATE.CANCELLED
        job.completion_date = get_todays_date_plus_days(0)
        job.latest_pending_task = None
        job.save()

        # For debugging purposes only.
        logger.info("Job was cancelled.")

        #----------------------------#
        # Enhance our output results #
        #----------------------------#
        validated_data['latest_pending_task'] = None

        # Return our results.
        return validated_data
