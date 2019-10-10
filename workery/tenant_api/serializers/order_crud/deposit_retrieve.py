# -*- coding: utf-8 -*-
import logging
import phonenumbers
from freezegun import freeze_time
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
from tenant_foundation.models import WorkOrder, WorkOrderDeposit


class WorkOrderDepositRetrieveSerializer(serializers.ModelSerializer):
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
