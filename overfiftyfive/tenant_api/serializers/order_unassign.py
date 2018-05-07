# -*- coding: utf-8 -*-
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
from rest_framework.authtoken.models import Token
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
    Order,
    OrderComment,
    Organization,
    TaskItem
)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


def cannot_be_zero_or_negative(value):
    if value <= 0:
        raise serializers.ValidationError('Please pick a reason from the dropdown.')
    return value


class OrderUnassignCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=Order.objects.all(), required=True)
    reason = serializers.IntegerField(required=True, validators=[cannot_be_zero_or_negative,])
    reason_other = serializers.CharField(required=True, allow_blank=True)
    additional_comment = serializers.CharField(required=True, allow_blank=True)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'reason',
            'reason_other',
            'additional_comment',
        )

    def validate(self, data):
        """
        Override the validator to provide additional custom validation based
        on our custom logic.

        1. If 'reason' == 1 then make sure 'reason_other' was inputted.
        """
        # CASE 1 - Other reason
        if data['reason'] == 1:
            reason_other = data['reason_other']
            if reason_other == "":
                raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))
        return data  # Return our data.

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # For debugging purposes only.
        print("INFO: Input at", str(validated_data))

        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        job = validated_data.get('job', None)
        reason = validated_data.get('reason', None)
        reason_other = validated_data.get('reason_other', None)
        additional_comment_text = validated_data.get('additional_comment', None)

        # #------------------------------------------#
        # Create any additional optional comments. #
        #------------------------------------------#
        if additional_comment_text:
            comment_obj = Comment.objects.create(
                created_by=self.context['user'],
                last_modified_by=self.context['user'],
                text=additional_comment_text
            )
            OrderComment.objects.create(
                about=job,
                comment=comment_obj,
            )

            # For debugging purposes only.
            print("INFO: Job comment created.")

        #----------------------------------------#
        # Lookup our Task(s) and close them all. #
        #----------------------------------------#
        task_items = TaskItem.objects.filter(
            job=job,
            is_closed=False
        )
        for task_item in task_items.all():
            print("INFO: Found task #", str(task_item.id))
            task_item.reason = reason
            task_item.reason_other = reason_other
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.save()
            print("INFO: Closed task #", str(task_item.id))

        # Update our job.
        job.associate = None
        job.save()

        # For debugging purposes only.
        print("INFO: Removed associate from job.")

        #---------------------------------------------#
        # Create a new task based on a new start date #
        #---------------------------------------------#
        next_task_item = TaskItem.objects.create(
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
        print("INFO: Assignment Task #", str(next_task_item.id), "was created b/c of unassignment.")

        # Assign our new variables and return the validated data.
        validated_data['id'] = next_task_item.id
        return validated_data
