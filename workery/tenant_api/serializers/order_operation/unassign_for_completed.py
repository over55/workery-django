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


class CompletedWorkOrderUnassignOperationSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), required=True)
    reason = serializers.CharField(required=True, allow_blank=False)
    latest_pending_task = serializers.ReadOnlyField()

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'reason',
            'latest_pending_task'
        )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        job = validated_data.get('job', None)
        comment_text = validated_data.get('reason', None)

        #---------------------------#
        # Create required comments. #
        #---------------------------#
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

        # For debugging purposes only.
        logger.info("Job reason comment created.")

        #---------------------------#
        # Close all previous tasks. #
        #---------------------------#
        for task_item in TaskItem.objects.filter(job=job, is_closed=False):
            task_item.is_closed = True
            task_item.closing_reason = 0
            task_item.closing_reason_other = _('Closed because job was unassigned.')
            task_item.created_by = self.context['user']
            task_item.last_modified_by = self.context['user']
            task_item.save()

        #---------------------------------------------#
        # Create a new task based on a new start date #
        #---------------------------------------------#
        task_item = TaskItem.objects.create(
            created_by=self.context['user'],
            last_modified_by=self.context['user'],
            type_of = ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID,
            due_date = job.start_date,
            is_closed = False,
            job = job,
            title = _('Assign an Associate'),
            description = _('Please assign an associate to this job.')
        )

        # For debugging purposes only.
        logger.info("Assignment Task #%(id)s was created b/c of unassignment." % {
            'id': str(task_item.id)
        })

        #------------------------------#
        # Assign our new ticket to job #
        #------------------------------#
        job.associate = None
        job.latest_pending_task = task_item
        job.state = WORK_ORDER_STATE.DECLINED
        job.save()

        # For debugging purposes only.
        logger.info("Job updated.")

        #----------------------------#
        # Enhance our output results #
        #----------------------------#
        validated_data['latest_pending_task'] = task_item.id

        # Return our results.
        return validated_data
