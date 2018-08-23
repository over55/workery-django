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


def get_end_of_month_date():
    """Return last day of this month"""
    import calendar
    today = timezone.now()
    last_day = calendar.mdays[today.month]
    return today.replace(day=last_day)


class AssignAssociateTaskOperationSerializer(serializers.Serializer):
    task_item = serializers.PrimaryKeyRelatedField(many=False, queryset=TaskItem.objects.all(), required=True)
    associate = serializers.PrimaryKeyRelatedField(many=False, queryset=Associate.objects.all(), required=True)
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
            'associate',
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

    def create_for_job(self, validated_data, task_item, associate, comment, state):
        # STEP 2 - Create our activity sheet item.
        obj = ActivitySheetItem.objects.create(
            job=task_item.job,
            associate=associate,
            comment=comment,
            state=state,
            created_by=self.context['user'],
        )

        # For debugging purposes only.
        logger.info("ActivitySheetItem was created.")

        if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED or state == ACTIVITY_SHEET_ITEM_STATE.PENDING:

            # STEP 3 - Update our job.
            obj.job.associate = associate
            obj.job.assignment_date = get_todays_date_plus_days()
            obj.job.save()

            # For debugging purposes only.
            logger.info("Associate assigned to Job.")

            # For debugging purposes only.
            logger.info("Found task #%(task_item)s" % {
                'task_item': str(task_item.id)
            })

            # STEP 4 - Update our TaskItem if job was accepted.
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.save()

            # For debugging purposes only.
            logger.info("Task #%(task_item)s was closed." % {
                'task_item': str(task_item.id)
            })

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

            # STEP 5 - Create our new task for following up.
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
            task_item.job.associate = None
            task_item.job.state = WORK_ORDER_STATE.DECLINED
            task_item.job.save()

        comment_obj = Comment.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            text=comment,
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public']
        )
        WorkOrderComment.objects.create(
            about=task_item.job,
            comment=comment_obj,
        )

        # For debugging purposes only.
        logger.info("Job comment created.")

        # STEP 5 - Assign our new variables and return the validated data.
        validated_data['id'] = obj.id
        return validated_data

    def create_for_ongoing_job(self, validated_data, task_item, associate, comment, state):
        # STEP 2 - Create our activity sheet item.
        obj = ActivitySheetItem.objects.create(
            job=None,
            ongoing_job=task_item.ongoing_job,
            associate=associate,
            comment=comment,
            state=state,
            created_by=self.context['user'],
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

            # For debugging purposes only.
            logger.info("Found task #%(task_item)s" % {
                'task_item': str(task_item.id)
            })

            # STEP 4 - Update our TaskItem if job was accepted.
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.save()

            # For debugging purposes only.
            logger.info("Task #%(task_item)s was closed." % {
                'task_item': str(task_item.id)
            })

            # Create the task message / time based on the `state`.
            title = None
            description = None
            due_date = None
            type_of = None
            if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED:
                title = _('48 hour follow up')
                description =  _('Please call up the client and confirm that the associate and client have agreed on scheduled meeting date in the future.')
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
                job = task_item.job,
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

            # Save our new task and job state updated.
            task_item.ongoing_job.save()

        else:
            task_item.ongoing_job.associate = None
            task_item.ongoing_job.state = ONGOING_WORK_ORDER_STATE.IDLE
            task_item.ongoing_job.save()

        comment_obj = Comment.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            text=comment,
            created_from = self.context['from'],
            created_from_is_public = self.context['from_is_public']
        )
        OngoingWorkOrderComment.objects.create(
            about=task_item.ongoing_job,
            comment=comment_obj,
        )

        # For debugging purposes only.
        logger.info("(Ongoing) Job comment created.")

        # STEP 5 - Assign our new variables and return the validated data.
        validated_data['id'] = obj.id
        return validated_data

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # STEP 1 - Get validated POST data.
        task_item = validated_data.get('task_item', None)
        associate = validated_data.get('associate', None)
        comment = validated_data.get('comment', None)
        state = validated_data.get('state', None)

        # CASE 1 OF 2: ONGOING JOBS
        if task_item.ongoing_job:
            return self.create_for_ongoing_job(validated_data, task_item, associate, comment, state)

        # CASE 2 OF 2: SINGLE TIME JOBS
        else:
            return self.create_for_job(validated_data, task_item, associate, comment, state)
