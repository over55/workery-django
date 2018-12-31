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
    ActivitySheetItem,
    Associate,
    WorkOrder,
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


class WorkOrderPostponeCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), required=True)
    reason = serializers.IntegerField(required=True, validators=[cannot_be_zero_or_negative,])
    reason_other = serializers.CharField(required=True, allow_blank=True)
    additional_comment = serializers.CharField(required=True, allow_blank=True)
    start_date = serializers.DateField(required=True, allow_null=False)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'reason',
            'reason_other',
            'additional_comment',
            'start_date',
        )

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        task_item = TaskItem.objects.filter(
            job=data['job'],
            is_closed=False
        ).order_by('due_date').first()
        if task_item is None:
            raise serializers.ValidationError(_("Task no longer exists, please go back to the list page."))
        return data

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
        start_date = validated_data.get('start_date', None)

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

        #------------------------#
        # Close the current task #
        #------------------------#
        task_item = TaskItem.objects.filter(
            job=job,
            is_closed=False
        ).order_by('due_date').first()

        # For debugging purposes only.
        logger.info("Found task #%(id)s." % {
            'id': str(task_item.id)
        })

        # Update our TaskItem.
        task_item.is_closed = True
        task_item.was_postponed = True
        task_item.closing_reason = reason
        task_item.closing_reason_other = reason_other
        task_item.last_modified_by = self.context['user']
        task_item.created_from = self.context['from']
        task_item.created_from_is_public = self.context['from_is_public']
        task_item.last_modified_by = self.context['user']
        task_item.save()

        # For debugging purposes only.
        logger.info("Task #%(id)s was closed b/c of postponement." % {
            'id': str(task_item.id)
        })

        #---------------------------------------------#
        # Create a new task based on a new start date #
        #---------------------------------------------#
        next_task_item = TaskItem.objects.create(
            type_of = task_item.type_of,
            title = task_item.title,
            description = task_item.description,
            due_date = start_date,
            is_closed = False,
            was_postponed = False,
            job = task_item.job,
            created_by = self.context['user'],
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public'],
            last_modified_by = self.context['user']
        )

        # For debugging purposes only.
        logger.info("Task #%(id)s was created b/c of postponement." % {
            'id': str(next_task_item.id)
        })

        # Attach our next job.
        job.latest_pending_task = next_task_item
        job.save()

        # Assign our new variables and return the validated data.
        validated_data['id'] = next_task_item.id
        return validated_data
