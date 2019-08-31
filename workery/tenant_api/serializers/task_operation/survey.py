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
    reason = serializers.IntegerField(required=False, validators=[cannot_be_zero_or_negative,])
    reason_other = serializers.CharField(required=False, allow_blank=True)
    comment = serializers.CharField(required=False, allow_blank=True)
    was_survey_conducted = serializers.BooleanField(required=True)
    no_survey_conducted_reason = serializers.BooleanField(required=False)
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
            'reason',
            'reason_other',
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
        if data['reason'] == 1:
            reason_other = data['reason_other']
            if reason_other == "":
                raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))

        # CASE 2 - Job done by associate
        elif data['reason'] == 4:
            pass #TODO: IMPLEMENT.

        # Return our data.
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """

        #--------------------#
        # Updated the output #
        #--------------------#
        # validated_data['id'] = obj.id
        return validated_data
