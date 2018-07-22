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


class CompletedWorkOrderCloseOperationSerializer(serializers.Serializer):
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
        if job.latest_pending_task:
            job.latest_pending_task.is_closed = True
            job.latest_pending_task.closing_reason = 0
            job.latest_pending_task.closing_reason_other = _('Closed because job was closed.')
            job.latest_pending_task.created_by = self.context['user']
            job.latest_pending_task.last_modified_by = self.context['user']
            job.latest_pending_task.save()

        #----------------#
        # Update the job #
        #----------------#
        job.state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
        job.latest_pending_task = None
        job.save()

        # For debugging purposes only.
        logger.info("Job updated.")

        #----------------------------#
        # Enhance our output results #
        #----------------------------#
        validated_data['latest_pending_task'] = None

        # Return our results.
        return validated_data
