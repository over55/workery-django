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


class ActivitySheetItemCreateSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=Order.objects.all(), required=True)
    associate = serializers.PrimaryKeyRelatedField(many=False, queryset=Associate.objects.all(), required=True)
    comment = serializers.CharField(required=True)
    has_accepted_job = serializers.BooleanField(required=True)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'associate',
            'comment',
            'has_accepted_job',
        )

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        task_item = TaskItem.objects.filter(
            type_of=ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID,
            job=data['job'],
            is_closed=False
        ).order_by('due_date').first()
        if task_item is None:
            raise serializers.ValidationError(_("Task no longer exists, please go back to the list page."))
        return data

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        # For debugging purposes only.
        print("INFO: Input at", str(validated_data))

        # STEP 1 - Get validated POST data.
        job = validated_data.get('job', None)
        associate = validated_data.get('associate', None)
        comment = validated_data.get('comment', None)
        has_accepted_job = validated_data.get('has_accepted_job', None)

        # STEP 2 - Create our activity sheet item.
        obj = ActivitySheetItem.objects.create(
            job=job,
            associate=associate,
            comment=comment,
            has_accepted_job=has_accepted_job,
            created_by=self.context['user'],
        )

        # For debugging purposes only.
        print("INFO: ActivitySheetItem was created.")

        if has_accepted_job:

            # STEP 3 - Update our job.
            obj.job.associate = associate
            obj.job.assignment_date = get_todays_date_plus_days()
            obj.job.save()

            # For debugging purposes only.
            print("INFO: Associate assigned to Job.")

            # STEP 4 - Lookup the most recent task which has not been closed
            #          for the particular job order.
            task_item = TaskItem.objects.filter(
                type_of=ASSIGNED_ASSOCIATE_TASK_ITEM_TYPE_OF_ID,
                job=job,
                is_closed=False
            ).order_by('due_date').first()

            # For debugging purposes only.
            print("INFO: Found task #", str(task_item.id))

            # STEP 4 - Update our TaskItem if job was accepted.
            task_item.is_closed = True
            task_item.last_modified_by = self.context['user']
            task_item.save()

            # For debugging purposes only.
            print("INFO: Task #", str(task_item.id), "was closed.")

            # STEP 5 - Create our new task for following up.
            next_task_item = TaskItem.objects.create(
                type_of = FOLLOW_UP_IS_JOB_COMPLETE_TASK_ITEM_TYPE_OF_ID,
                title = _('48 hour follow up'),
                description = _('Please call up the client and confirm that the associate and client have agreed on scheduled meeting date in the future.'),
                due_date = get_todays_date_plus_days(2),
                is_closed = False,
                job = task_item.job,
                created_by = self.context['user'],
                last_modified_by = self.context['user']
            )

            # For debugging purposes only.
            print("INFO: Task #", str(next_task_item.id), "was created.")

        # STEP 5 - Assign our new variables and return the validated data.
        validated_data['id'] = obj.id
        return validated_data
