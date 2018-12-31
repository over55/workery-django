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
    WORK_ORDER_STATE,
    WorkOrderComment,
    Organization,
    TaskItem
)


logger = logging.getLogger(__name__)


class WorkOrderReopenCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), required=True)
    reason = serializers.CharField(required=True, allow_blank=False)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'reason',
        )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        job = validated_data.get('job', None)
        reason = validated_data.get('reason', None)

        #---------------------------#
        # Close all previous tasks. #
        #---------------------------#
        if job.latest_pending_task:
            job.latest_pending_task.is_closed = True
            job.latest_pending_task.closing_reason = 0
            job.latest_pending_task.closing_reason_other = _('Closed because re-opending job.')
            job.latest_pending_task.last_modified_by = self.context['user']
            job.latest_pending_task.last_modified_by = self.context['user']
            job.latest_pending_task.save()

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

        #------------------------------------------#
        # Create any additional optional comments. #
        #------------------------------------------#
        if reason:
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                text=reason,
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public']
            )
            WorkOrderComment.objects.create(
                about=job,
                comment=comment_obj,
            )

            # For debugging purposes only.
            logger.info("Job comment created.")

        #--------------------------#
        # Update the `job` status. #
        #--------------------------#
        # Update our job to be in a `declined` state.
        job.associate = None
        job.state = WORK_ORDER_STATE.NEW
        job.latest_pending_task = task_item
        job.save()

        # For debugging purposes only.
        logger.info("Re-opened job.")

        # Return the validated results.
        return validated_data
