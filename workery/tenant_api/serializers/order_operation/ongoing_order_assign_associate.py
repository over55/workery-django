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
    ACTIVITY_SHEET_ITEM_STATE,
    ActivitySheetItem,
    Associate,
    WorkOrder,
    OngoingWorkOrder,
    WORK_ORDER_STATE,
    WorkOrderComment,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrderComment,
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


def get_end_of_month_date():
    """Return last day of this month"""
    import calendar
    today = timezone.now()
    last_day = calendar.mdays[today.month]
    return today.replace(day=last_day)


class OngoingWorkOrderAssignAssociateOperationSerializer(serializers.Serializer):
    ongoing_job = serializers.PrimaryKeyRelatedField(many=False, queryset=OngoingWorkOrder.objects.all(), required=True)
    associate = serializers.PrimaryKeyRelatedField(many=False, queryset=Associate.objects.all(), required=True)
    comment = serializers.CharField(required=True)
    state = serializers.CharField(
        required=True,
        error_messages={
            "invalid": "Please pick either 'Yes', 'No', or 'Pending' choice."
        }
    )
    latest_pending_task = serializers.ReadOnlyField()

    # Meta Information.
    class Meta:
        fields = (
            'ongoing_job',
            'associate',
            'comment',
            'state',
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
        # STEP 1 - Get validated POST data.
        ongoing_job = validated_data.get('ongoing_job', None)
        associate = validated_data.get('associate', None)
        comment = validated_data.get('comment', None)
        state = validated_data.get('state', None)

        #---------------------------------#
        # Close all the TaskItem objects. #
        #---------------------------------#
        for task_item in TaskItem.objects.filter(ongoing_job=ongoing_job, is_closed=False):
            task_item.last_modified_by = self.context['user']
            task_item.last_modified_from = self.context['from']
            task_item.last_modified_from_is_public = self.context['from_is_public']
            task_item.is_closed = True
            task_item.closing_reason = 1  # (Other - choice.)
            task_item.closing_reason_other = 'Closed because master job was closed.'
            task_item.save()

        # STEP 2 - Create our activity sheet item.
        obj = ActivitySheetItem.objects.create(
            job=None,
            ongoing_job=ongoing_job,
            associate=associate,
            comment=comment,
            state=state,
            created_by=self.context['user'],
            created_from=self.context['from'],
            created_from_is_public=self.context['from_is_public'],
        )

        # For debugging purposes only.
        logger.info("ActivitySheetItem was created.")

        if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED or state == ACTIVITY_SHEET_ITEM_STATE.PENDING:

            # STEP 3 - Update our job.
            obj.ongoing_job.associate = associate
            obj.ongoing_job.assignment_date = get_todays_date_plus_days()
            obj.ongoing_job.save()

            # For debugging purposes only.
            logger.info("Associate assigned to Job.")

            # Create the task message / time based on the `state`.
            title = None
            description = None
            due_date = None
            type_of = None
            if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED:
                title = _('48 hour follow up')
                description =  _('Please call the Associate and confirm that they have scheduled a meeting date with the client.')
                due_date = get_todays_date_plus_days(2)
                type_of = FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID
                # title = _('Ongoing Job Update')
                # description = _('Please review an ongoing job and fill in how many visits in previous month.')
                # due_date = get_end_of_month_date()
                # type_of = UPDATE_ONGOING_JOB_TASK_ITEM_TYPE_OF_ID
            elif state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
                title = _('Pending')
                description = _('Please contact the Associate to confirm if they want the job.')
                due_date = get_todays_date_plus_days(1)
                type_of = FOLLOW_UP_DID_ASSOCIATE_ACCEPT_JOB_TASK_ITEM_TYPE_OF_ID

            # STEP 5 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = type_of,
                title = title,
                description = description,
                due_date = due_date,
                is_closed = False,
                job = None,
                ongoing_job = ongoing_job,
                created_by = self.context['user'],
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public']
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created." % {
                'id': str(next_task_item.id)
            })

            # Attached our new TaskItem to the Job.
            ongoing_job.latest_pending_task = next_task_item

            # Change state
            if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED:
                ongoing_job.state = ONGOING_WORK_ORDER_STATE.RUNNING
            if state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
                ongoing_job.state = ONGOING_WORK_ORDER_STATE.IDLE

            # Save our new task and job state updated.
            ongoing_job.save()

        else:
            ongoing_job.associate = None
            ongoing_job.state = ONGOING_WORK_ORDER_STATE.IDLE
            ongoing_job.save()

        comment_obj = Comment.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            text=comment,
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public']
        )
        OngoingWorkOrderComment.objects.create(
            about=ongoing_job,
            comment=comment_obj,
        )

        # For debugging purposes only.
        logger.info("(Ongoing) Job comment created.")

        # STEP 5 - Assign our new variables and return the validated data.
        validated_data['id'] = obj.id
        return validated_data
