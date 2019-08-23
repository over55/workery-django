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
    WorkOrder,
    ONGOING_WORK_ORDER_STATE,
    OngoingWorkOrder,
    SkillSet,
    Tag,
    TaskItem
)


logger = logging.getLogger(__name__)


class WorkOrderFinancialUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkOrder
        fields = (
            'invoice_service_fee',
            'invoice_ids',
            'invoice_service_fee_payment_date',
            'invoice_date',
            'invoice_quote_amount',
            'invoice_labour_amount',
            'invoice_material_amount',
            'invoice_quoted_labour_amount',
            'invoice_quoted_material_amount',
            'invoice_total_quote_amount',
            'invoice_tax_amount',
            'invoice_total_amount',
            'invoice_service_fee_amount',
            'invoice_actual_service_fee_amount_paid',
            'state',
            'invoice_balance_owing_amount',
            'visits',
        )

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        instance.invoice_service_fee = validated_data.get('invoice_service_fee', instance.invoice_service_fee)
        instance.invoice_ids = validated_data.get('invoice_ids', instance.invoice_ids)
        instance.invoice_service_fee_payment_date = validated_data.get('invoice_service_fee_payment_date', instance.invoice_service_fee_payment_date)
        instance.invoice_date = validated_data.get('invoice_date', instance.invoice_date)
        instance.invoice_quote_amount = validated_data.get('invoice_quote_amount', instance.invoice_quote_amount)
        instance.invoice_labour_amount = validated_data.get('invoice_labour_amount', instance.invoice_labour_amount)
        instance.invoice_material_amount = validated_data.get('invoice_material_amount', instance.invoice_material_amount)
        instance.invoice_quoted_labour_amount = validated_data.get('invoice_quoted_labour_amount', instance.invoice_quoted_labour_amount)
        instance.invoice_quoted_material_amount = validated_data.get('invoice_quoted_material_amount', instance.invoice_quoted_material_amount)
        instance.invoice_total_quote_amount = validated_data.get('invoice_total_quote_amount', instance.invoice_total_quote_amount)
        instance.invoice_tax_amount = validated_data.get('invoice_tax_amount', instance.invoice_tax_amount)
        instance.invoice_total_amount = validated_data.get('invoice_total_amount', instance.invoice_total_amount)
        instance.invoice_service_fee_amount = validated_data.get('invoice_service_fee_amount', instance.invoice_service_fee_amount)
        instance.invoice_actual_service_fee_amount_paid = validated_data.get('invoice_actual_service_fee_amount_paid', instance.invoice_actual_service_fee_amount_paid)
        instance.state = validated_data.get('state', instance.state)
        instance.invoice_balance_owing_amount = validated_data.get('invoice_balance_owing_amount', instance.invoice_balance_owing_amount)
        instance.visits = validated_data.get('visits', instance.visits)
        instance.save()
        logger.info("Updated order object.")
        return instance
