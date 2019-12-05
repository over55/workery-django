# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID, WORKERY_APP_DEFAULT_MONEY_CURRENCY
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


def cannot_be_zero_or_negative(value):
    if value <= 0:
        raise serializers.ValidationError('Please pick a reason from the dropdown.')
    return value


def cannot_be_negative(value):
    if value < 0:
        raise serializers.ValidationError('Please enter an amount which is not negative!')
    return value



class WorkOrderCloseCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), required=True)
    was_successfully_finished = serializers.BooleanField(required=True,)
    completion_date = serializers.DateField(required=False, allow_null=True,)
    reason = serializers.IntegerField(required=False, validators=[cannot_be_zero_or_negative,], allow_null=True,)
    reason_other = serializers.CharField(required=False, allow_blank=True)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'was_successfully_finished',
            'completion_date',
            'reason',
            'reason_other',
        )

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        request = self.context['request']
        tenant = request.tenant
        user_id = request.user.id
        from_ip = request.client_ip
        from_ip_is_public = request.client_ip_is_routable

        #--------------------------#
        # Get validated POST data. #
        #--------------------------#
        job = validated_data.get('job', None)
        was_successfully_finished = validated_data.get('was_successfully_finished', None)
        completion_date = validated_data.get('completion_date', None)
        reason = validated_data.get('reason', None)
        reason_other = validated_data.get('reason_other', None)

        # -------------------------
        # ---      DETAILS      ---
        # -------------------------
        # (a) Object details.
        if was_successfully_finished:
            job.state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
        else:
            job.state = WORK_ORDER_STATE.CANCELLED
        job.completion_date = completion_date

        # (b) System details.
        job.last_modified_by_id = user_id
        job.last_modified_from = from_ip
        job.last_modified_from_is_public = from_ip_is_public
        job.save()

        # For debugging purposes only.
        logger.info("Job was updated.")

        # ---------------------
        # --- JOB IS CLOSED ---
        # ---------------------
        if was_successfully_finished:
            #---------------#
            # Close the job #
            #---------------#
            # STEP 1 - Close the job.
            job.closing_reason = reason
            job.closing_reason_other = reason_other
            job.last_modified_by_id = user_id
            job.state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
            job.completion_date = get_todays_date_plus_days(0)
            job.latest_pending_task = None

            # STEP 4 - Save all our changes.
            job.save()

            # For debugging purposes only.
            logger.info("Job was completed.")

            # Run the command which will process more advanced fields pertaining to
            # the process.
            from_ip_is_public = 1 if from_ip_is_public == True else 0
            call_command('process_paid_order', tenant.schema_name, job.id, user_id, from_ip, from_ip_is_public, verbosity=0)

        # ------------------------
        # --- JOB IS CANCELLED ---
        # ------------------------
        else:
            # Close the job.
            job.closing_reason = reason
            job.closing_reason_other = reason_other
            job.last_modified_by_id = user_id
            job.state = WORK_ORDER_STATE.CANCELLED
            job.completion_date = get_todays_date_plus_days(0)
            job.latest_pending_task = None
            job.save()

            # For debugging purposes only.
            logger.info("Job was cancelled.")

            tasks = TaskItem.objects.filter(Q(job=job) & Q(is_closed=False))
            for task in tasks:
                task.is_closed=True
                task.last_modified_by_id = user_id
                task.last_modified_from = from_ip
                task.last_modified_from_is_public = from_ip_is_public
                task.save()

        # raise serializers.ValidationError({ # For debugging purposes only. Do not delete, just uncomment.
        #     'error': 'Stop caused by programmer.',
        # })

        # validated_data['id'] = obj.id
        return validated_data
