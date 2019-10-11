# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation import constants
from tenant_api.serializers.skill_set import SkillSetListCreateSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    WorkOrderComment,
    WORK_ORDER_STATE,
    WorkOrder,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    SkillSet,
    Tag,
    TaskItem,
    WorkOrderDeposit
)


logger = logging.getLogger(__name__)


class WorkOrderDepositListCreateSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(many=False, queryset=WorkOrder.objects.all(), allow_null=True)
    paid_at = serializers.DateField()
    deposit_method = serializers.IntegerField()
    deposit_method_label = serializers.ReadOnlyField(source='get_pretty_deposit_method')
    paid_to = serializers.IntegerField()
    paid_to_label = serializers.ReadOnlyField(source='get_pretty_paid_to')
    paid_for = serializers.IntegerField()
    paid_for_label = serializers.ReadOnlyField(source='get_pretty_paid_for')
    created_at = serializers.ReadOnlyField()
    created_by = serializers.ReadOnlyField(source='created_by.get_full_name')
    last_modified_at = serializers.ReadOnlyField()
    last_modified_by = serializers.ReadOnlyField(source='last_modified_by.get_full_name')

    class Meta:
        model = WorkOrderDeposit
        fields = (
            'id',
            'order',
            'paid_at',
            'deposit_method',
            'deposit_method_label',
            'paid_to',
            'paid_to_label',
            'paid_for',
            'paid_for_label',
            'amount',
            'created_at',
            'created_by',
            'last_modified_at',
            'last_modified_by'
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'order',
            'created_by',
            'last_modified_by',
        )
        return queryset

    def create(self, validated_data):
        #---------------------------------------
        # Get the user inputs from the request.
        #---------------------------------------

        order = validated_data.get('order', None)
        paid_at = validated_data.get('paid_at', None)
        deposit_method = validated_data.get('deposit_method', None)
        paid_to = validated_data.get('paid_to', None)
        paid_for = validated_data.get('paid_for', None)
        amount = validated_data.get('amount', None)

        #---------------------------------------
        # Create our `OngoingWorkOrder` objects.
        #---------------------------------------

        deposit = WorkOrderDeposit.objects.create(
            order=order,
            paid_at=paid_at,
            deposit_method=deposit_method,
            paid_to=paid_to,
            paid_for=paid_for,
            amount=amount,
            created_by = self.context['created_by'],
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
            last_modified_by = self.context['created_by'],
            last_modified_from = self.context['created_from'],
            last_modified_from_is_public = self.context['created_from_is_public'],
        )

        #---------------------------------------
        # Calculate the new deposit amount.
        #---------------------------------------

        deposits = WorkOrderDeposit.objects.filter(order=order)
        amount = 0
        for deposit in deposits.all():
            amount += deposit.amount.amount

        order.invoice_deposit_amount = Money(amount, constants.WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        order.invoice_amount_due = order.invoice_total_amount - order.invoice_deposit_amount
        order.last_modified_by = self.context['created_by']
        order.last_modified_from = self.context['created_from']
        order.last_modified_from_is_public = self.context['created_from_is_public']
        order.save()

        # Return our validated data.
        return deposit
