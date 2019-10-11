# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
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


class OrderCompletionTaskOperationSerializer(serializers.Serializer):
    task_item = serializers.PrimaryKeyRelatedField(many=False, queryset=TaskItem.objects.all(), required=True)

    # Step 2 of 4
    was_completed = serializers.BooleanField(required=True)
    reason = serializers.IntegerField(required=False, validators=[cannot_be_zero_or_negative,])
    reason_other = serializers.CharField(required=False, allow_blank=True, allow_null=True,)
    completion_date = serializers.DateField(required=True)

    # Step 3 of 4
    invoice_date = serializers.DateField(required=False,allow_null=True,)
    invoice_ids = serializers.CharField(required=False, allow_blank=True, allow_null=True,)
    invoice_quote_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_labour_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_material_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_tax_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_total_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_service_fee_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])

    # Step 4 of 4
    comment = serializers.CharField(required=False, allow_blank=True)

    # Meta Information.
    class Meta:
        fields = (
            'task_item',

            # Step 2 of 4
            'was_completed',
            'reason',
            'reason_other',
            'completion_date',

            # Step 3 of 4
            'invoice_date',
            'invoice_ids',
            'invoice_quote_amount',
            'invoice_labour_amount',
            'invoice_material_amount',
            'invoice_tax_amount',
            'invoice_total_amount',
            'invoice_service_fee_amount'

            # Step 4 of 4
            'comment',
        )

    def validate(self, data):
        """
        Override the validator to provide additional custom validation based
        on our custom logic.

        1. If 'reason' == 1 then make sure 'reason_other' was inputted.
        2. If 'reason' == 4 then make sure the Customer survey fields where inputted.
        """
        # CASE 1 - Other reason
        if data['reason'] == 1:
            reason_other = data['reason_other']
            if reason_other == "":
                raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))

        # CASE 2 - Job done by associate
        elif data['reason'] == 4:
            pass #TODO: IMPLEMENT.

        task_item = data.get('task_item', None)
        if task_item.is_closed:
            raise serializers.ValidationError(_("Task has been previously processed by %(name)s and cannot be edited." % {
                'name': str(task_item.last_modified_by)
            }))

        # Return our data.
        return data

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #--------------------------#
        # Get validated POST data. #
        #--------------------------#
        task_item = validated_data.get('task_item', None)

        # Step 2 of 4
        was_completed = validated_data.get('was_completed', None)
        reason = validated_data.get('reason', None)
        reason_other = validated_data.get('reason_other', None)
        completion_date = validated_data.get('completion_date', None)

        # Step 3 of 4
        invoice_date = validated_data.get('invoice_date', None)
        invoice_ids = validated_data.get('invoice_ids',  0)
        invoice_quote_amount = validated_data.get('invoice_quote_amount',  0)
        invoice_labour_amount = validated_data.get('invoice_labour_amount',  0)
        invoice_material_amount = validated_data.get('invoice_material_amount',  0)
        invoice_tax_amount = validated_data.get('invoice_tax_amount',  0)
        invoice_total_amount = validated_data.get('invoice_total_amount',  0)
        invoice_service_fee_amount = validated_data.get('invoice_service_fee_amount',  0)

        # Step 4 of 4
        comment_text = validated_data.get('comment', None)

        # --------------------------
        # --- WORK ORDER DETAILS ---
        # --------------------------
        # Step 2 of 4
        if was_completed:
            task_item.job.state = WORK_ORDER_STATE.COMPLETED_BUT_UNPAID
            logger.info("Job was completed put unpaid.")  # For debugging purposes only.
        else:
            task_item.job.closing_reason = reason
            task_item.job.closing_reason_other = reason_other
            task_item.job.state = WORK_ORDER_STATE.CANCELLED
            logger.info("Job was cancelled.")  # For debugging purposes only.
        task_item.job.completion_date = completion_date
        task_item.job.last_modified_by = self.context['user']
        task_item.job.latest_pending_task = None

        # Step 3 of 4
        task_item.job.invoice_date = invoice_date
        task_item.job.invoice_ids = invoice_ids
        task_item.job.invoice_quote_amount = Money(invoice_quote_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        task_item.job.invoice_labour_amount = Money(invoice_labour_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        task_item.job.invoice_material_amount = Money(invoice_material_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        task_item.job.invoice_tax_amount = Money(invoice_tax_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        task_item.job.invoice_total_amount = Money(invoice_total_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        task_item.job.invoice_service_fee_amount = Money(invoice_service_fee_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)

        # Misc.
        task_item.job.last_modified_by = self.context['user']
        task_item.job.last_modified_from = self.context['from']
        task_item.job.last_modified_from_is_public = self.context['from_is_public']

        # Save the task item with our newest updates.
        task_item.job.save()

        # For debugging purposes only.
        logger.info("Job financials where updated.")

        # Step 4 of 4
        if comment_text != None and comment_text != "":
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                text=comment_text,
                created_from = self.context['from'],
                created_from_is_public = self.context['from_is_public']
            )
            WorkOrderComment.objects.create(
                about=task_item.job,
                comment=comment_obj,
            )

            # For debugging purposes only.
            logger.info("Job comment created.")

        #----------------------------------------#
        # Lookup our Task(s) and close them all. #
        #----------------------------------------#
        task_items = TaskItem.objects.filter(
            job=task_item.job,
            is_closed=False
        )
        for task_item in task_items.all():
            logger.info("Found task # #%(id)s ." % {
                'id': str(task_item.id)
            })
            task_item.reason = reason
            task_item.reason_other = reason_other
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.save()
            logger.info("Task #%(id)s was closed." % {
                'id': str(task_item.id)
            })

        # ------------------------
        # --- SURVEY TASK ITEM ---
        # ------------------------
        # Generate our task title.
        title = _('Survey')

        # Rational: We want to ask the customer after 7 days AFTER the completion date.
        meeting_date = get_todays_date_plus_days(7)

        # STEP 5 - Create our new task for survey.
        next_task_item = TaskItem.objects.create(
            type_of = FOLLOW_UP_DID_CUSTOMER_REVIEW_ASSOCIATE_AFTER_JOB_TASK_ITEM_TYPE_OF_ID,
            title = title,
            description = _('Please call client and review the associate.'),
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

        # The following code will add our new item to the job.
        task_item.job.latest_pending_task = next_task_item
        task_item.job.last_modified_by = self.context['user']
        task_item.job.last_modified_from = self.context['from']
        task_item.job.last_modified_from_is_public = self.context['from_is_public']
        task_item.job.save()

        #--------------------#
        # Updated the output #
        #--------------------#
        # validated_data['id'] = obj.id
        return validated_data
