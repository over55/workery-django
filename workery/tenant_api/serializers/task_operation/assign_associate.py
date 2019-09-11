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
        task_item = data.get('task_item', None)
        if task_item is None:
            raise serializers.ValidationError(_("Task no longer exists, please go back to the list page."))
        if task_item.is_closed:
            raise serializers.ValidationError(_("Task has been previously processed by %(name)s and cannot be edited." % {
                'name': str(task_item.last_modified_by)
            }))
        return data

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # STEP 1 - Get validated POST data.
        task_item = validated_data.get('task_item')
        associate = validated_data.get('associate')
        comment = validated_data.get('comment')
        state = validated_data.get('state')

        # STEP 2 - Create our activity sheet item.
        activity_sheet_item = ActivitySheetItem.objects.create(
            job=task_item.job,
            associate=associate,
            comment=comment,
            state=state,
            created_by=self.context['created_by'],
            created_from=self.context['created_from'],
            created_from_is_public=self.context['created_from_is_public'],
        )

        # For debugging purposes only.
        logger.info("ActivitySheetItem was created.")

        if state == ACTIVITY_SHEET_ITEM_STATE.ACCEPTED or state == ACTIVITY_SHEET_ITEM_STATE.PENDING:

            # STEP 3 - Update our job.
            # (a) Object Details
            activity_sheet_item.job.associate = associate
            activity_sheet_item.job.assignment_date = get_todays_date_plus_days()

            # (b) System Details
            activity_sheet_item.job.last_modified_by = self.context['created_by']
            activity_sheet_item.job.last_modified_from = self.context['created_from']
            activity_sheet_item.job.last_modified_from_is_public = self.context['created_from_is_public']

            activity_sheet_item.job.save()

            # For debugging purposes only.
            logger.info("Associate assigned to Job.")

            # For debugging purposes only.
            logger.info("Found task #%(task_item)s" % {
                'task_item': str(task_item.id)
            })

            # STEP 4 - Update our TaskItem job was accepted or pending.
            # (a) Object Details
            task_item.is_closed = True

            # (b) System Details
            task_item.last_modified_by = self.context['created_by']
            task_item.last_modified_from = self.context['created_from']
            task_item.last_modified_from_is_public = self.context['created_from_is_public']

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
                description = _('Please call the Associate and confirm that they have scheduled a meeting date with the client.')
                due_date = get_todays_date_plus_days(2)
                type_of = FOLLOW_UP_DID_ASSOCIATE_AND_CUSTOMER_AGREED_TO_MEET_TASK_ITEM_TYPE_OF_ID
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
                created_by=self.context['created_by'],
                created_from=self.context['created_from'],
                created_from_is_public=self.context['created_from_is_public'],
                last_modified_by=self.context['created_by'],
                last_modified_from = self.context['created_from'],
                last_modified_from_is_public = self.context['created_from_is_public'],
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

            # STEP 6: Assign associate job.
            if task_item.job.is_ongoing and task_item.job.ongoing_work_order:
                task_item.job.ongoing_work_order.associate = associate
                task_item.job.ongoing_work_order.last_modified_by = self.context['created_by']
                task_item.job.ongoing_work_order.last_modified_from = self.context['created_from']
                task_item.job.ongoing_work_order.last_modified_from_is_public = self.context['created_from_is_public']
                task_item.job.ongoing_work_order.save()

        else:
            task_item.job.associate = None
            task_item.job.state = WORK_ORDER_STATE.DECLINED
            task_item.job.save()

            # Unassign associate job.
            if task_item.job.is_ongoing and task_item.job.ongoing_work_order:
                task_item.job.ongoing_work_order.associate = None
                task_item.job.ongoing_work_order.last_modified_by = self.context['created_by']
                task_item.job.ongoing_work_order.last_modified_from = self.context['created_from']
                task_item.job.ongoing_work_order.last_modified_from_is_public = self.context['created_from_is_public']
                task_item.job.ongoing_work_order.save()

        comment_obj = Comment.objects.create(
            created_by=self.context['created_by'],
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
            last_modified_by=self.context['created_by'],
            last_modified_from = self.context['created_from'],
            last_modified_from_is_public = self.context['created_from_is_public'],
            text=comment,
        )
        WorkOrderComment.objects.create(
            about=task_item.job,
            comment=comment_obj,
        )

        # For debugging purposes only.
        logger.info("Job comment created.")

        # STEP 5 - Assign our new variables and return the validated data.
        validated_data['id'] = activity_sheet_item.id
        return validated_data
