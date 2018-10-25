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
    OngoingWorkOrderComment,
    ONGOING_WORK_ORDER_STATE,
    WORK_ORDER_STATE,
    WorkOrderComment,
    Organization,
    TaskItem
)


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class FollowUpPendingTaskOperationSerializer(serializers.Serializer):
    task_item = serializers.PrimaryKeyRelatedField(many=False, queryset=TaskItem.objects.all(), required=True)
    comment = serializers.CharField(required=True)
    state = serializers.CharField(
        required=True,
        error_messages={
            "invalid": "Please pick either 'Yes', 'No', or 'Pending' choice."
        }
    )

    # Meta Information.
    class Meta:
        fields = (
            'task_item',
            'comment',
            'state',
        )

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        task_item = data['task_item']
        if task_item is None:
            raise serializers.ValidationError(_("Task no longer exists, please go back to the list page."))
        return data

    def create_for_job(self, validated_data, task_item, comment, state):

        # Attached our comment.
        comment_obj = Comment.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            text=comment,
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public']
        )
        WorkOrderComment.objects.create(
            about = task_item.job,
            comment = comment_obj,
        )

        # For debugging purposes only.
        logger.info("Attached comment to Job.")

        # STEP 4 - Lookup our current activity sheet and set the status of
        #          the activity sheet based on the users decision.
        current_activity_sheet_item = ActivitySheetItem.objects.filter(
            job = task_item.job,
            associate = task_item.job.associate,
        ).first()

        # DEFENSIVE CODE: If the `ActivitySheetItem` was not found then
        #                 we error.
        if current_activity_sheet_item is None:
            raise serializers.ValidationError(_("Activity sheet was not found. This was probably because you already closed this task."))

        current_activity_sheet_item.state = state
        current_activity_sheet_item.last_modified_by = self.context['user']
        current_activity_sheet_item.save()

        if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED or state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
            '''
            Accepted or Pending
            '''

            # STEP 5 - Update our job.
            current_activity_sheet_item.job.associate = task_item.job.associate
            current_activity_sheet_item.job.assignment_date = get_todays_date_plus_days()
            current_activity_sheet_item.job.save()

            # For debugging purposes only.
            logger.info("Associate assigned to Job.")

            # Create the task message / time based on the `state`.
            title = None
            description = None
            due_date = None
            type_of = None
            if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED:
                title = _('48 hour follow up')
                description = _('Please call up the client and confirm that the associate and client have agreed on scheduled meeting date in the future.')
                due_date = get_todays_date_plus_days(2)
                type_of = FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID
            elif state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
                title = _('Pending')
                description = _('Please contact the Associate to confirm if they want the job.')
                due_date = get_todays_date_plus_days(1)
                type_of = FOLLOW_UP_DID_ASSOCIATE_ACCEPT_JOB_TASK_ITEM_TYPE_OF_ID

            # STEP 6 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = type_of,
                title = title,
                description = description,
                due_date = due_date,
                is_closed = False,
                job = task_item.job,
                created_by = self.context['user'],
                last_modified_by = self.context['user']
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created." % {
                'id': str(next_task_item.id)
            })

            # Attached our new TaskItem to the Job.
            task_item.job.latest_pending_task = next_task_item

            # Change state
            if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED:
                task_item.job.state = WORK_ORDER_STATE.IN_PROGRESS
            if state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
                task_item.job.state = WORK_ORDER_STATE.PENDING

            # Save our new task and job state updated.
            task_item.job.save()

        else:
            '''
            Declined
            '''

            #---------------------------------------------#
            # Create a new task based on a new start date #
            #---------------------------------------------#
            next_task_item = TaskItem.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                type_of = ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID,
                due_date = task_item.job.start_date,
                is_closed = False,
                job = task_item.job,
                title = _('Assign an Associate'),
                description = _('Please assign an associate to this job.')
            )

            # For debugging purposes only.
            logger.info("Assignment Task #%(id)s was created b/c of unassignment." % {
                'id': str(next_task_item.id)
            })

            # Attach our next job.
            task_item.job.associate = None
            task_item.job.state = WORK_ORDER_STATE.DECLINED
            task_item.job.latest_pending_task = next_task_item
            task_item.job.save()

        # STEP 5 - Assign our new variables and return the validated data.
        validated_data['id'] = current_activity_sheet_item.id
        return validated_data

    def create_for_ongoing_job(self, validated_data, task_item, comment, state):

        # Attached our comment.
        comment_obj = Comment.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            text=comment,
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public']
        )
        OngoingWorkOrderComment.objects.create(
            about = task_item.ongoing_job,
            comment = comment_obj,
        )

        # For debugging purposes only.
        logger.info("Attached comment to Ongoing-Job.")

        # STEP 4 - Lookup our current activity sheet and set the status of
        #          the activity sheet based on the users decision.
        current_activity_sheet_item = ActivitySheetItem.objects.filter(
            ongoing_job = task_item.ongoing_job,
            associate = task_item.ongoing_job.associate,
        ).first()
        current_activity_sheet_item.state = state
        current_activity_sheet_item.last_modified_by = self.context['user']
        current_activity_sheet_item.save()

        if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED or state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
            '''
            Accepted or Pending
            '''

            # STEP 5 - Update our ongoing_job.
            current_activity_sheet_item.ongoing_job.associate = task_item.ongoing_job.associate
            current_activity_sheet_item.ongoing_job.assignment_date = get_todays_date_plus_days()
            current_activity_sheet_item.ongoing_job.save()

            # For debugging purposes only.
            logger.info("Associate assigned to Job.")

            # Create the task message / time based on the `state`.
            title = None
            description = None
            due_date = None
            type_of = None
            if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED:
                title = _('48 hour follow up')
                description = _('Please call up the client and confirm that the associate and client have agreed on scheduled meeting date in the future.')
                due_date = get_todays_date_plus_days(2)
                type_of = FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID
            elif state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
                title = _('Pending')
                description = _('Please contact the Associate to confirm if they want the ongoing job.')
                due_date = get_todays_date_plus_days(1)
                type_of = FOLLOW_UP_DID_ASSOCIATE_ACCEPT_JOB_TASK_ITEM_TYPE_OF_ID

            # STEP 6 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = type_of,
                title = title,
                description = description,
                due_date = due_date,
                is_closed = False,
                ongoing_job = task_item.ongoing_job,
                created_by = self.context['user'],
                last_modified_by = self.context['user']
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created." % {
                'id': str(next_task_item.id)
            })

            # Attached our new TaskItem to the Job.
            task_item.ongoing_job.latest_pending_task = next_task_item

            # Change state
            if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED:
                task_item.ongoing_job.state = ONGOING_WORK_ORDER_STATE.RUNNING
            if state == ACTIVITY_SHEET_ITEM_STATE.PENDING:
                task_item.ongoing_job.state = ONGOING_WORK_ORDER_STATE.IDLE

            # Save our new task and ongoing_job state updated.
            task_item.ongoing_job.save()

        else:
            '''
            Declined
            '''

            #---------------------------------------------#
            # Create a new task based on a new start date #
            #---------------------------------------------#
            next_task_item = TaskItem.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                type_of = ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID,
                due_date = task_item.ongoing_job.start_date,
                is_closed = False,
                ongoing_job = task_item.ongoing_job,
                title = _('Assign an Associate'),
                description = _('Please assign an associate to this ongoing job.')
            )

            # For debugging purposes only.
            logger.info("Assignment Task #%(id)s was created b/c of unassignment." % {
                'id': str(next_task_item.id)
            })

            # Attach our next ongoing_job.
            task_item.ongoing_job.associate = None
            task_item.ongoing_job.state = ONGOING_WORK_ORDER_STATE.IDLE
            task_item.ongoing_job.latest_pending_task = next_task_item
            task_item.ongoing_job.save()

        # STEP 5 - Assign our new variables and return the validated data.
        validated_data['id'] = current_activity_sheet_item.id
        return validated_data

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # STEP 1 - Get validated POST data.
        task_item = validated_data.get('task_item', None)
        comment = validated_data.get('comment', None)
        state = validated_data.get('state', None)

        # STEP 3 - Update our TaskItem to be closed.
        task_item.is_closed = True
        task_item.last_modified_by = self.context['user']
        task_item.save()

        # For debugging purposes only.
        logger.info("Task #%(task_item)s was closed." % {
            'task_item': str(task_item.id)
        })

        if task_item.ongoing_job:
            return self.create_for_ongoing_job(validated_data, task_item, comment, state)
        else:
            return self.create_for_job(validated_data, task_item, comment, state)
