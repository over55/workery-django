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
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    ActivitySheetItem,
    Associate,
    Customer,
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


class TransferWorkOrderOperationSerializer(serializers.Serializer):
    job = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), required=True, allow_null=False)
    associate = serializers.IntegerField(required=True, allow_null=True)
    customer = serializers.IntegerField(required=True, allow_null=True)
    reason = serializers.CharField(required=True, allow_blank=False)

    # Meta Information.
    class Meta:
        fields = (
            'job',
            'associate',
            'customer',
            'reason',
        )

    def validate_associate(self, value):
        """
        Check that the associate exists in the database.
        """
        if value is not None:
            if Associate.objects.filter(id=value).exists() is False:
                raise serializers.ValidationError("Associate does not exist.")
        return value

    def validate_customer(self, value):
        """
        Check that the customer exists in the database.
        """
        if value is not None:
            if Customer.objects.filter(id=value).exists() is False:
                raise serializers.ValidationError("Customer does not exist.")
        return value

    def validate(self, data):
        """
        Override the final validation to include additional extras. Any
        validation error will be populated in the "non_field_errors" field.
        """
        # Confirm that we have an assignment task open.
        associate = data.get('associate', None)
        customer = data.get('customer', None)
        if associate is None and customer is None:
            raise serializers.ValidationError(_("At minimum you must select either associate or customer."))
        return data

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-------------------------#
        # Get validated POST data #
        #-------------------------#
        job = validated_data.get('job', None)
        associate = validated_data.get('associate', None)
        customer = validated_data.get('customer', None)
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

        #------------------------------#
        # Transfer `Associate` object. #
        #------------------------------#
        if associate:
            # (1) Process `WorkOrder` objects.
            associate = Associate.objects.get(id=associate)
            job.associate = associate
            job.last_modified_by = self.context['user']
            job.last_modified_from = self.context['from']
            job.last_modified_from_is_public = self.context['from_is_public']
            job.save()

            # (2) Process `ActivitySheetItem` objects.
            for activity_sheet_item in ActivitySheetItem.objects.filter(job=job).iterator():
                activity_sheet_item.associate = associate
                activity_sheet_item.save()

        #-----------------------------#
        # Transfer `Customer` object. #
        #-----------------------------#
        if customer:
            # (1) Process `WorkOrder` objects.
            customer = Customer.objects.get(id=customer)
            job.customer = customer
            job.last_modified_by = self.context['user']
            job.last_modified_from = self.context['from']
            job.last_modified_from_is_public = self.context['from_is_public']
            job.save()

        # Return our results.
        return validated_data
