# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
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
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from shared_api.custom_fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID, WORKERY_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    ActivitySheetItem,
    Associate,
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
    reason = serializers.IntegerField(required=True, validators=[cannot_be_zero_or_negative,])
    reason_other = serializers.CharField(required=True, allow_blank=True)
    additional_comment = serializers.CharField(required=True, allow_blank=True)
    was_job_satisfactory = serializers.BooleanField(required=True)
    was_job_finished_on_time_and_on_budget = serializers.BooleanField(required=True)
    was_associate_punctual = serializers.BooleanField(required=True)
    was_associate_professional = serializers.BooleanField(required=True)
    would_customer_refer_our_organization = serializers.BooleanField(required=True)
    invoice_date = serializers.DateField(required=True)
    invoice_id = serializers.IntegerField(required=False, validators=[cannot_be_negative,])
    invoice_quote_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_labour_amount = serializers.FloatField(required=True, validators=[cannot_be_negative,])
    invoice_material_amount = serializers.FloatField(required=True, validators=[cannot_be_negative,])
    invoice_tax_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_total_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])
    invoice_service_fee_amount = serializers.FloatField(required=False, validators=[cannot_be_negative,])

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'reason',
            'reason_other',
            'additional_comment',
            'was_job_satisfactory',
            'was_job_finished_on_time_and_on_budget',
            'was_associate_punctual',
            'was_associate_professional',
            'would_customer_refer_our_organization',
            'invoice_date',
            'invoice_id',
            'invoice_quote_amount',
            'invoice_labour_amount',
            'invoice_material_amount',
            'invoice_tax_amount',
            'invoice_total_amount',
            'invoice_service_fee_amount'
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

        # Return our data.
        return data

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #--------------------------#
        # Get validated POST data. #
        #--------------------------#
        job = validated_data.get('job', None)
        reason = validated_data.get('reason', None)
        reason_other = validated_data.get('reason_other', None)
        additional_comment_text = validated_data.get('additional_comment', None)
        was_job_satisfactory = validated_data.get('was_job_satisfactory', False)
        was_job_finished_on_time_and_on_budget = validated_data.get('was_job_finished_on_time_and_on_budget', False)
        was_associate_punctual = validated_data.get('was_associate_punctual', False)
        was_associate_professional = validated_data.get('was_associate_professional', False)
        would_customer_refer_our_organization = validated_data.get('would_customer_refer_our_organization', False)
        invoice_date = validated_data.get('invoice_date', None)
        invoice_id = validated_data.get('invoice_id',  0)
        invoice_quote_amount = validated_data.get('invoice_quote_amount',  0)
        invoice_labour_amount = validated_data.get('invoice_labour_amount',  0)
        invoice_material_amount = validated_data.get('invoice_material_amount',  0)
        invoice_tax_amount = validated_data.get('invoice_tax_amount',  0)
        invoice_total_amount = validated_data.get('invoice_total_amount',  0)
        invoice_service_fee_amount = validated_data.get('invoice_service_fee_amount',  0)

        # -------------------------
        # --- FINANCIAL DETAILS ---
        # -------------------------
        job.invoice_date = invoice_date
        job.invoice_id = invoice_id
        job.invoice_quote_amount = Money(invoice_quote_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        job.invoice_labour_amount = Money(invoice_labour_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        job.invoice_material_amount = Money(invoice_material_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        job.invoice_tax_amount = Money(invoice_tax_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        job.invoice_total_amount = Money(invoice_total_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        job.invoice_service_fee_amount = Money(invoice_service_fee_amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        job.save()

        # For debugging purposes only.
        logger.info("Job financials where updated.")

        #------------------------------------------#
        # Create any additional optional comments. #
        #------------------------------------------#
        if additional_comment_text:
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                text=additional_comment_text,
                created_from = self.context['created_from'],
                created_from_is_public = self.context['created_from_is_public']
            )
            WorkOrderComment.objects.create(
                about=job,
                comment=comment_obj,
            )

            # For debugging purposes only.
            logger.info("Job comment created.")

        #----------------------------------------#
        # Lookup our Task(s) and close them all. #
        #----------------------------------------#
        task_items = TaskItem.objects.filter(
            job=job,
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
        # --- JOB IS CANCELLED ---
        # ------------------------
        if reason != 4:
            # Close the job.
            job.closing_reason = reason
            job.closing_reason_other = reason_other
            job.last_modified_by = self.context['user']
            job.is_cancelled = True
            job.completion_date = get_todays_date_plus_days(0)
            job.latest_pending_task = None
            job.save()

            # For debugging purposes only.
            logger.info("Job was cancelled.")

        # ---------------------
        # --- JOB IS CLOSED ---
        # ---------------------
        else:
            #---------------#
            # Close the job #
            #---------------#
            # STEP 1 - Close the job.
            job.closing_reason = reason
            job.closing_reason_other = reason_other
            job.last_modified_by = self.context['user']
            job.is_cancelled = False
            job.completion_date = get_todays_date_plus_days(0)
            job.latest_pending_task = None

            # STEP 2 - Save the results.
            job.was_job_satisfactory = was_job_satisfactory
            job.was_job_finished_on_time_and_on_budget = was_job_finished_on_time_and_on_budget
            job.was_associate_punctual = was_associate_punctual
            job.was_associate_professional = was_associate_professional
            job.would_customer_refer_our_organization = would_customer_refer_our_organization

            #-------------------------#
            # Compute associate score #
            #-------------------------#
            # STEP 3 - Compute the score.
            job.score = 0
            job.score += int(was_job_satisfactory)
            job.score += int(was_job_finished_on_time_and_on_budget)
            job.score += int(was_associate_punctual)
            job.score += int(was_associate_professional)
            job.score += int(would_customer_refer_our_organization)
            job.save()

            # For debugging purposes only.
            logger.info("Job was completed.")

            # STEP 4 - Update the associate score by re-computing the average
            #          score and saving it with the profile.
            jobs_count = WorkOrder.objects.filter(
                is_cancelled = False,
                associate = job.associate,
                closing_reason = 4,
            ).count()
            summation_results = WorkOrder.objects.filter(
                is_cancelled = False,
                associate = job.associate,
                closing_reason = 4,
            ).aggregate(Sum('score'))

            score_sum = summation_results['score__sum']
            total_score = score_sum / jobs_count

            # For debugging purposes only.
            logger.info("Assocate is calculated as: %(total_score)s" % {
                'total_score': str(total_score)
            })

        #---------------------------------#
        # Ongoing jobs require new ticket #
        #---------------------------------#
        if job.is_ongoing:
            follow_up_days_number = int(job.follow_up_days_number)
            next_task_item = TaskItem.objects.create(
                type_of = FOLLOW_UP_CUSTOMER_SURVEY_TASK_ITEM_TYPE_OF_ID,
                title = _('7 day follow up'),
                description = _('Please call up the client and perform the satisfaction survey.'),
                due_date = get_todays_date_plus_days(follow_up_days_number),
                is_closed = False,
                job = job,
                created_by = self.context['user'],
                last_modified_by = self.context['user']
            )

            # For debugging purposes only.
            logger.info("Task #%(id)s was created." % {
                'id': str(next_task_item.id)
            })

            # Attach our next job.
            job.latest_pending_task = next_task_item
            job.save()

        #--------------------#
        # Updated the output #
        #--------------------#
        # validated_data['id'] = obj.id
        return validated_data
