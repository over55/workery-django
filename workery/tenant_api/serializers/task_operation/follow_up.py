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
    WORK_ORDER_STATE,
    WorkOrder,
    WorkOrderComment,
    Organization,
    TaskItem
)


logger = logging.getLogger(__name__)


def get_date_plus_days(dt, days=0):
    """Returns the current date plus paramter number of days."""
    return dt + timedelta(days=days)


class FollowUpTaskOperationSerializer(serializers.Serializer):
    task_item = serializers.PrimaryKeyRelatedField(many=False, queryset=TaskItem.objects.all(), required=True)
    comment = serializers.CharField(required=False)
    has_agreed_to_meet = serializers.BooleanField(required=True)
    meeting_date = serializers.DateField(required=False)

    # Meta Information.
    class Meta:
        fields = (
            'task_item',
            'comment',
            'has_agreed_to_meet',
            'meeting_date'
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

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # Defensive Code - If no date was specified then we assume 7 days from today.
        today_plus_seven = get_date_plus_days(timezone.now(), 7)

        # STEP 1 - Get validated POST data.
        task_item = validated_data.get('task_item', None)
        comment_text = validated_data.get('comment', None)
        has_agreed_to_meet = validated_data.get('has_agreed_to_meet', None)
        meeting_date = validated_data.get('meeting_date', today_plus_seven)

        # STEP 2 - If the user has submitted an optional comment for the job
        #          then we will include it.
        if comment_text:
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public'],
                last_modified_by=self.context['user'],
                last_modified_from = self.context['from'],
                last_modified_from_is_public = self.context['from_is_public'],
                text=comment_text,
            )
            WorkOrderComment.objects.create(
                about = task_item.job,
                comment = comment_obj,
            )

        # STEP 3 - Update our TaskItem by closing all previous open tasks.
        #----------------------------------------#
        # Lookup our Task(s) and close them all. #
        #----------------------------------------#
        task_items = TaskItem.objects.filter(
            job=task_item.job,
            is_closed=False
        )
        for item in task_items.iterator():
            logger.info("Found task # #%(id)s ." % {
                'id': str(item.id)
            })
            item.is_closed = True
            item.last_modified_by = self.context['user']
            item.last_modified_from = self.context['from']
            item.last_modified_from_is_public = self.context['from_is_public']
            item.save()
            logger.info("Task #%(id)s was closed." % {
                'id': str(item.id)
            })

        # For debugging purposes only.
        logger.info("Task #%(id)s was closed" % {
            'id': str(task_item.id)
        })

        # STEP 4 - Check to see if associate and client agreed to meet...
        if has_agreed_to_meet:

            # Generate our task title.
            title = _('Survey')
            if task_item.job:
                if task_item.job.is_ongoing or task_item.ongoing_job != None:
                    title = _('Survey / Ongoing')

            # Rational: We want to ask the customer 24 hours AFTER the client meeting data.
            meeting_date = get_date_plus_days(meeting_date, 1)

            # STEP 5 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                title = title,
                description = _('Please call up the client and perform the satisfaction survey.'),
                due_date = meeting_date,
                is_closed = False,
                job = task_item.job,
                created_by = self.context['user'],
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public'],
                last_modified_by = self.context['user'],
                last_modified_from = self.context['from'],
                last_modified_from_is_public = self.context['from_is_public'],
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created" % {
                'id': str(next_task_item.id)
            })

            # Attach our next job.
            task_item.job.latest_pending_task = next_task_item

            # Change state.
            task_item.job.state = WORK_ORDER_STATE.IN_PROGRESS

            # Updated the start date to either right now or the agreed upon
            # date between associate and client.
            task_item.job.start_date = meeting_date

            # System details update.
            task_item.job.last_modified_by = self.context['user']
            task_item.job.last_modified_from = self.context['from']
            task_item.job.last_modified_from_is_public = self.context['from_is_public']

            # Save our changes.
            task_item.job.save()

        else:

            # STEP 5 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID,
                title = _('48 hour follow up - 24 hour check'),
                description = _('It appears a previous 48 hour follow was not completed. This is a 24 hour follow up. Please call the Associate and confirm that they have scheduled a meeting date with the client.'),
                due_date = get_date_plus_days(timezone.now(), 1), # 24 hour version instead of 48 hour version!
                is_closed = False,
                job = task_item.job,
                created_by = self.context['user'],
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public'],
                last_modified_by = self.context['user'],
                last_modified_from = self.context['from'],
                last_modified_from_is_public = self.context['from_is_public'],
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created" % {
                'id': str(next_task_item.id)
            })

            # Attach our next job.
            # (a) Object details
            task_item.job.latest_pending_task = next_task_item
            task_item.job.state = WORK_ORDER_STATE.IN_PROGRESS

            # (b) System details.
            # System details update.
            task_item.job.last_modified_by = self.context['user']
            task_item.job.last_modified_from = self.context['from']
            task_item.job.last_modified_from_is_public = self.context['from_is_public']

            task_item.job.save()

        # # STEP 6 - Assign our new variables and return the validated data.
        # validated_data['id'] = obj.id
        return validated_data
