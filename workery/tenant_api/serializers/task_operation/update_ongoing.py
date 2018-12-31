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
from djmoney.money import Money
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.utils import get_first_date_for_this_month
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




class UpdateOngoingTaskOperationSerializer(serializers.Serializer):
    task_item = serializers.PrimaryKeyRelatedField(many=False, queryset=TaskItem.objects.all(), required=True)
    number_of_visits = serializers.IntegerField(required=True)

    # Meta Information.
    class Meta:
        fields = (
            'task_item',
            'number_of_visits',
        )

    # def validate(self, data):
    #     """
    #     Override the final validation to include additional extras. Any
    #     validation error will be populated in the "non_field_errors" field.
    #     """
    #     # Confirm that we have an assignment task open.
    #     task_item = TaskItem.objects.filter(
    #         type_of=FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID,
    #         job=data['job'],
    #         is_closed=False
    #     ).order_by('due_date').first()
    #     if task_item is None:
    #         raise serializers.ValidationError(_("Task no longer exists, please go back to the list page."))
    #     return data

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
        )

        # Update our ongoing job to have our closed tasks.
        ongoing_job.closed_orders.add(order)


    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # STEP 1 - Get validated POST data.
        task_item = validated_data.get('task_item', None)
        number_of_visits = validated_data.get('number_of_visits', 0)

        # Go through the number of visits and create a new WorkOrder per visit.
        for visit in range(0, number_of_visits):
            self.create_work_order_from_ongoing_job(task_item.ongoing_job)

        # Update the `OngoingWorkOrder` to have the user whom edited it plus
        # remove our `TaskItem` instance from it.
        task_item.ongoing_job.latest_pending_task = None
        task_item.ongoing_job.last_modified_by =self.context['user']
        task_item.ongoing_job.last_modified_from =self.context['from']
        task_item.ongoing_job.last_modified_from_is_public =self.context['from_is_public']
        task_item.ongoing_job.save()

        # Update the task to be completed.
        task_item.is_closed = True
        task_item.last_modified_by = self.context['user']
        task_item.last_modified_from = self.context['from']
        task_item.last_modified_from_is_public = self.context['from_is_public']
        task_item.save()

        return validated_data
