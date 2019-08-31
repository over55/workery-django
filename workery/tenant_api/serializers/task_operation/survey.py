# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
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


#TODO: INTEGRATE


class SurveyTaskOperationSerializer(serializers.Serializer):
    task_item = serializers.PrimaryKeyRelatedField(many=False, queryset=TaskItem.objects.all(), required=True)
    comment = serializers.CharField(required=False, allow_blank=True)
    was_survey_conducted = serializers.BooleanField(required=True)
    no_survey_conducted_reason = serializers.IntegerField(required=False)
    no_survey_conducted_reason_other = serializers.CharField(required=False, allow_blank=True)
    was_job_satisfactory = serializers.BooleanField(required=False)
    was_job_finished_on_time_and_on_budget = serializers.BooleanField(required=False)
    was_associate_punctual = serializers.BooleanField(required=False)
    was_associate_professional = serializers.BooleanField(required=False)
    would_customer_refer_our_organization = serializers.BooleanField(required=False)


    # Meta Information.
    class Meta:
        fields = (
            'task_item',
            'comment',
            'was_survey_conducted',
            'no_survey_conducted_reason',
            'no_survey_conducted_reason_other',
            'was_job_satisfactory',
            'was_job_finished_on_time_and_on_budget',
            'was_associate_punctual',
            'was_associate_professional',
            'would_customer_refer_our_organization',
        )

    def validate(self, data):
        """
        Override the validator to provide additional custom validation based
        on our custom logic.

        1. If 'reason' == 1 then make sure 'reason_other' was inputted.
        2. If 'reason' == 4 then make sure the Customer survey fields where inputted.
        """
        # CASE 1 - Other reason
        if data.get('no_survey_conducted_reason') == 1:
            reason_other = data.get("no_survey_conducted_reason_other")
            if reason_other == "":
                raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))

        # Return our data.
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """

        # ------------------
        # --- GET INPUTS ---
        # ------------------

        task_item = validated_data.get('task_item', None)
        comment_text = validated_data.get('comment', None)
        was_survey_conducted = validated_data.get('was_survey_conducted', None)
        no_survey_conducted_reason = validated_data.get('no_survey_conducted_reason', None)
        no_survey_conducted_reason_other = validated_data.get('no_survey_conducted_reason_other', None)
        was_job_satisfactory = validated_data.get('was_job_satisfactory', None)
        was_job_finished_on_time_and_on_budget = validated_data.get('was_job_finished_on_time_and_on_budget', None)
        was_associate_punctual = validated_data.get('was_associate_punctual', None)
        was_associate_professional = validated_data.get('was_associate_professional', None)
        would_customer_refer_our_organization = validated_data.get('would_customer_refer_our_organization', None)

        # --------------------------
        # --- WORK ORDER DETAILS ---
        # --------------------------

        if was_survey_conducted:
            task_item.job.was_job_satisfactory = was_job_satisfactory
            task_item.job.was_job_finished_on_time_and_on_budget = was_job_finished_on_time_and_on_budget
            task_item.job.was_associate_punctual = was_associate_punctual
            task_item.job.was_associate_professional = was_associate_professional
            task_item.job.would_customer_refer_our_organization = would_customer_refer_our_organization
        else:
            task_item.job.no_survey_conducted_reason = no_survey_conducted_reason
            task_item.job.no_survey_conducted_reason_other = no_survey_conducted_reason_other
        task_item.job.was_survey_conducted = was_survey_conducted
        task_item.job.last_modified_by = self.context['user']
        task_item.job.last_modified_from = self.context['from']
        task_item.job.last_modified_from_is_public = self.context['from_is_public']
        task_item.job.save()

        # For debugging purposes only.
        logger.info("Job was updated.")

        # Step 4 of 4
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

        # ------------------------------
        # --- UPDATE ASSOCIATE SCORE ---
        # ------------------------------
        if was_survey_conducted:
            # Compute the score.
            task_item.job.score = 0
            task_item.job.score += int(was_job_satisfactory)
            task_item.job.score += int(was_job_finished_on_time_and_on_budget)
            task_item.job.score += int(was_associate_punctual)
            task_item.job.score += int(was_associate_professional)
            task_item.job.score += int(would_customer_refer_our_organization)
            task_item.job.save()

            # Update the associate score by re-computing the average
            # score and saving it with the profile.
            jobs_count = WorkOrder.objects.filter(
                Q(associate = task_item.job.associate) &
                Q(was_survey_conducted=True)
            ).count()
            summation_results = WorkOrder.objects.filter(
                Q(associate = task_item.job.associate) &
                Q(was_survey_conducted=True)
            ).aggregate(Sum('score'))

            score_sum = summation_results['score__sum']
            total_score = score_sum / jobs_count

            # For debugging purposes only.
            logger.info("Assocate score calculated is: %(total_score)s" % {
                'total_score': str(total_score)
            })

        return validated_data
