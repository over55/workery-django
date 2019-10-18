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
from tenant_api.serializers.tag import TagListCreateSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Comment,
    WorkOrderComment,
    WORK_ORDER_STATE,
    WorkOrderInvoice,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    SkillSet,
    Tag,
    TaskItem
)


logger = logging.getLogger(__name__)


class WorkOrderInvoiceThirdSectionUpdateSerializer(serializers.ModelSerializer):

    invoice_quote_days = serializers.IntegerField(required=True, write_only=True,)
    invoice_quote_date = serializers.DateField(required=True, write_only=True,)
    invoice_customers_approval = serializers.CharField(required=True, write_only=True,)
    line01_notes = serializers.CharField(required=True, write_only=True,)
    line02_notes = serializers.CharField(required=False, write_only=True, allow_null=True,)
    payment_date = serializers.DateField(required=True, write_only=True,)
    is_cash = serializers.BooleanField(required=False, write_only=True,)
    is_cheque = serializers.BooleanField(required=False, write_only=True,)
    is_debit = serializers.BooleanField(required=False, write_only=True,)
    is_credit = serializers.BooleanField(required=False, write_only=True,)
    is_other = serializers.BooleanField(required=False, write_only=True,)
    client_signature = serializers.CharField(required=True, write_only=True,)
    associate_sign_date = serializers.DateField(required=True, write_only=True,)
    associate_signature = serializers.CharField(required=True, write_only=True,)

    class Meta:
        model = WorkOrderInvoice
        fields = (
            'invoice_quote_days',
            'invoice_quote_date',
            'invoice_customers_approval',
            'line01_notes',
            'line02_notes',
            'payment_date',
            'is_cash',
            'is_cheque',
            'is_debit',
            'is_credit',
            'is_other',
            'client_signature',
            'associate_sign_date',
            'associate_signature'
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.invoice_quote_days = validated_data.get('invoice_quote_days', instance.invoice_quote_days)
        instance.invoice_quote_date = validated_data.get('invoice_quote_date', instance.invoice_quote_date)
        instance.invoice_customers_approval = validated_data.get('invoice_customers_approval', instance.invoice_customers_approval)
        instance.line_01_notes = validated_data.get('line01_notes', instance.line_01_notes)
        instance.line_02_notes = validated_data.get('line02_notes', instance.line_02_notes)
        instance.payment_date = validated_data.get('payment_date', instance.payment_date)
        instance.is_cash = validated_data.get('is_cash', instance.is_cash)
        instance.is_cheque = validated_data.get('is_cheque', instance.is_cheque)
        instance.is_debit = validated_data.get('is_debit', instance.is_debit)
        instance.is_credit = validated_data.get('is_credit', instance.is_credit)
        instance.is_other = validated_data.get('is_other', instance.is_other)
        instance.client_signature = validated_data.get('client_signature', instance.client_signature)
        instance.associate_sign_date = validated_data.get('associate_sign_date', instance.associate_sign_date)
        instance.associate_signature = validated_data.get('associate_signature', instance.associate_signature)
        instance.revision_version += 1
        instance.save()
        logger.info("Updated third section.")

        return instance
