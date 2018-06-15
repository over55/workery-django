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
    ActivitySheetItem,
    Associate,
    WORK_ORDER_STATE,
    WorkOrder,
    WorkOrderComment,
    Organization,
    TaskItem
)


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class WorkOrderCompleteCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), required=True)
    comment = serializers.CharField(required=False)
    has_agreed_to_meet = serializers.BooleanField(required=True)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'comment',
            'has_agreed_to_meet',
        )

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        task_item = TaskItem.objects.filter(
            type_of=FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID,
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
        # STEP 1 - Get validated POST data.
        job = validated_data.get('job', None)
        comment_text = validated_data.get('comment', None)
        has_agreed_to_meet = validated_data.get('has_agreed_to_meet', None)

        # STEP 2 - If the user has submitted an optional comment for the job
        #          then we will include it.
        if comment_text:
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                text=comment_text,
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public']
            )
            WorkOrderComment.objects.create(
                about=job,
                comment=comment_obj,
            )

        # STEP 3 - Lookup the most recent task which has not been closed
        #          for the particular job order.
        task_item = TaskItem.objects.filter(
            type_of=FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID,
            job=job,
            is_closed=False
        ).order_by('due_date').first()

        # For debugging purposes only.
        logger.info("Found task #%(id)s was closed" % {
            'id': str(task_item.id)
        })

        # STEP 4 - Update our TaskItem if job was accepted.
        task_item.is_closed = True
        task_item.last_modified_by = self.context['user']
        task_item.save()

        # For debugging purposes only.
        logger.info("Task #%(id)s was closed" % {
            'id': str(task_item.id)
        })

        if has_agreed_to_meet:

            # STEP 5 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                title = _('7 day follow up'),
                description = _('Please call up the client and perform the satisfaction survey.'),
                due_date = get_todays_date_plus_days(7),
                is_closed = False,
                job = task_item.job,
                created_by = self.context['user'],
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public'],
                last_modified_by = self.context['user']
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created" % {
                'id': str(next_task_item.id)
            })

            # Attach our next job.
            job.latest_pending_task = next_task_item
            job.state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
            job.save()

        else:

            # STEP 5 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                title = _('24 hour follow up'),
                description = _('Please call up the client and confirm that the associate and client have agreed on scheduled meeting date in the future.'),
                due_date = get_todays_date_plus_days(1),
                is_closed = False,
                job = task_item.job,
                created_by = self.context['user'],
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public'],
                last_modified_by = self.context['user']
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created" % {
                'id': str(next_task_item.id)
            })

            # Attach our next job.
            job.latest_pending_task = next_task_item
            job.state = WORK_ORDER_STATE.IN_PROGRESS
            job.save()

        # # STEP 6 - Assign our new variables and return the validated data.
        # validated_data['id'] = obj.id
        return validated_data
