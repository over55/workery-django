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
    ActivitySheetItem,
    ACTIVITY_SHEET_ITEM_STATE,
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


class OngoingWorkOrderUnassignCreateSerializer(serializers.Serializer):
    ongoing_job = serializers.PrimaryKeyRelatedField(many=False, queryset=OngoingWorkOrder.objects.all(), required=True)
    reason = serializers.CharField(required=True, allow_blank=False)
    latest_pending_task = serializers.ReadOnlyField()

    # Meta Information.
    class Meta:
        fields = (
            'ongoing_job',
            'reason',
            'latest_pending_task'
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
        ongoing_job = validated_data.get('ongoing_job', None)
        reason = validated_data.get('reason', None)

        activity_sheets = ActivitySheetItem.objects.filter(
            ongoing_job=ongoing_job,
            associate=ongoing_job.associate
        )
        for activity_sheet in activity_sheets.all():
            activity_sheet.state = ACTIVITY_SHEET_ITEM_STATE.DECLINED
            activity_sheet.save()

        #------------------------------------------#
        # Create any additional optional comments. #
        #------------------------------------------#
        comment_obj = Comment.objects.create(
            text=reason,
            created_from = self.context['from'],
            created_by=self.context['user'],
            created_from_is_public = self.context['from_is_public']
        )
        OngoingWorkOrderComment.objects.create(
            about=ongoing_job,
            comment=comment_obj,
        )

        # For debugging purposes only.
        logger.info("Job comment created.")

        #----------------------------------------#
        # Lookup our Task(s) and close them all. #
        #----------------------------------------#
        for task_item in TaskItem.objects.filter(ongoing_job=ongoing_job, is_closed=False):
            logger.info("Found task #%(id)s." % {
                'id': str(task_item.id)
            })
            task_item.reason = 1
            task_item.reason_other = _('Because associate was unassigned.')
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.last_modified_from = self.context['from']
            task_item.last_modified_from_is_public = self.context['from_is_public']
            task_item.save()
            logger.info("Closed task #%(id)s." % {
                'id': str(task_item.id)
            })


        #-------------------------#
        # Update the ongoing job. #
        #-------------------------#
        # Update our job to be in a `idle` state.
        ongoing_job.associate = None
        ongoing_job.state = ONGOING_WORK_ORDER_STATE.IDLE
        ongoing_job.save()

        # For debugging purposes only.
        logger.info("Update ongoing job.")

        #---------------------------------------------#
        # Create a new task based on a new start date #
        #---------------------------------------------#
        next_task_item = TaskItem.objects.create(
            created_by=self.context['user'],
            type_of = ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID,
            due_date = ongoing_job.start_date,
            is_closed = False,
            ongoing_job = ongoing_job,
            title = _('Assign an Associate'),
            description = _('Please assign an associate to this ongoing job.')
        )

        # For debugging purposes only.
        logger.info("Assignment Task #%(id)s was created b/c of unassignment." % {
            'id': str(next_task_item.id)
        })

        # Attach our next job.
        ongoing_job.latest_pending_task = next_task_item
        ongoing_job.save()

        # Assign our new variables and return the validated data.
        validated_data['latest_pending_task'] = next_task_item.id
        return validated_data
