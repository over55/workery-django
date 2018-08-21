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
from djmoney.money import Money
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_api.custom_fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.utils import get_first_date_for_this_month
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    Associate,
    WorkOrder,
    WORK_ORDER_STATE,
    ONGOING_WORK_ORDER_STATE,
    Organization,
    OngoingWorkOrder,
    OngoingWorkOrderComment,
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


class OngoingWorkOrderCreationWizardOperationSerializer(serializers.Serializer):
    ongoing_job = serializers.PrimaryKeyRelatedField(many=False, queryset=OngoingWorkOrder.objects.all(), required=True)
    number_of_visits = serializers.IntegerField(required=True)

    # Meta Information.
    class Meta:
        fields = (
            'ongoing_job',
            'number_of_visits',
        )

    def create_work_order_from_ongoing_job(self, ongoing_job):
        first_date_dt = get_first_date_for_this_month()
        franchise =self.context['franchise']
        default_amount = Money(0, franchise.currency)

        order = WorkOrder.objects.create(
            customer = ongoing_job.customer,
            associate = ongoing_job.associate,
            assignment_date = first_date_dt,
            is_ongoing = True,
            closing_reason=0,
            closing_reason_other=None,
            start_date = first_date_dt,
            completion_date=first_date_dt,
            hours=0,
            # last_modified_by =self.context['user'],
            created_by =self.context['user'],
            created_from =self.context['from'],
            created_from_is_public =self.context['from_is_public'],
            invoice_service_fee_payment_date=first_date_dt,
            invoice_service_fee=None,
            invoice_service_fee_amount=default_amount,
            type_of = ongoing_job.type_of,
            state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID,
            was_job_satisfactory = True,
            was_job_finished_on_time_and_on_budget = True,
            was_associate_punctual = True,
            was_associate_professional = True,
            would_customer_refer_our_organization = True,
            score = True,
            invoice_id = 0,
            description = ongoing_job.description,
        )

        # Update our ongoing job to have our closed tasks.
        ongoing_job.closed_orders.add(order)

        # Add skill sets.
        for skill_set in ongoing_job.skill_sets.all():
            order.skill_sets.add(skill_set)

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        ongoing_job = validated_data.get('ongoing_job', None)
        number_of_visits = validated_data.get('number_of_visits', None)

        # Go through the number of visits and create a new WorkOrder per visit.
        for visit in range(0, number_of_visits):
            self.create_work_order_from_ongoing_job(ongoing_job)

        # Update the `OngoingWorkOrder` to have the user whom edited it plus
        # remove our `TaskItem` instance from it.
        ongoing_job.latest_pending_task = None
        ongoing_job.last_modified_by =self.context['user']
        ongoing_job.last_modified_from =self.context['from']
        ongoing_job.last_modified_from_is_public =self.context['from_is_public']
        ongoing_job.save()

        # Update the task to be completed.
        task_items = TaskItem.objects.filter(ongoing_job=ongoing_job)
        for task_item in task_items.all():
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.last_modified_from = self.context['from']
            task_item.last_modified_from_is_public = self.context['from_is_public']
            task_item.save()

        # Returned validated data.
        return validated_data
