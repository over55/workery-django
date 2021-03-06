# -*- coding: utf-8 -*-
import logging
import phonenumbers
from datetime import datetime, timedelta
from dateutil import tz
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.core.management import call_command
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

    invoice_service_fee_payment_date = serializers.DateField(required=False, allow_null=True,)
    completion_date = serializers.DateField(required=False, allow_null=True,)

    class Meta:
        model = WorkOrder
        fields = (
            'invoice_paid_to',
            'invoice_service_fee',
            'invoice_ids',
            'invoice_service_fee_payment_date',
            'invoice_date',
            'invoice_quote_amount',
            'invoice_labour_amount',
            'invoice_material_amount',
            'invoice_other_costs_amount',
            'invoice_quoted_labour_amount',
            'invoice_quoted_material_amount',
            'invoice_quoted_other_costs_amount',
            'invoice_total_quote_amount',
            'invoice_tax_amount',
            'invoice_total_amount',
            'invoice_deposit_amount',
            'invoice_amount_due',
            'invoice_service_fee_amount',
            'invoice_actual_service_fee_amount_paid',
            'state',
            'invoice_balance_owing_amount',
            'visits',
            'completion_date',
        )

    def validate_invoice_service_fee_payment_date(self, value):
        """
        Custom validation to deal with instance where:
        (1) If state is "completed_and_paid" and this field is `None` then error
        (2) Else if state is anything besides "completed_and_paid" then accept
            `None` is accepted in this field.
        """
        request = self.context.get('request')
        state = request.data.get('state', None)
        if state:
            if state == WORK_ORDER_STATE.COMPLETED_AND_PAID:
                if value == None:
                    raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_completion_date(self, value):
        """
        Custom validation to deal with instance where:
        (1) If state is "completed_and_paid" and this field is `None` then error
        (2) Else if state is anything besides "completed_and_paid" then accept
            `None` is accepted in this field.
        """
        request = self.context.get('request')
        state = request.data.get('state', None)
        if state:
            if state == WORK_ORDER_STATE.COMPLETED_AND_PAID:
                if value == None:
                    raise serializers.ValidationError("This field may not be blank.")
        return value

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        request = self.context.get('request')
        tenant = request.tenant
        user_id = request.user.id
        from_ip = request.client_ip
        from_ip_is_public = request.client_ip_is_routable
        instance.invoice_paid_to = validated_data.get('invoice_paid_to', instance.invoice_paid_to)
        instance.invoice_service_fee = validated_data.get('invoice_service_fee', instance.invoice_service_fee)
        instance.invoice_ids = validated_data.get('invoice_ids', instance.invoice_ids)
        instance.invoice_service_fee_payment_date = validated_data.get('invoice_service_fee_payment_date', instance.invoice_service_fee_payment_date)
        instance.invoice_date = validated_data.get('invoice_date', instance.invoice_date)
        instance.invoice_quote_amount = validated_data.get('invoice_quote_amount', instance.invoice_quote_amount)
        instance.invoice_labour_amount = validated_data.get('invoice_labour_amount', instance.invoice_labour_amount)
        instance.invoice_material_amount = validated_data.get('invoice_material_amount', instance.invoice_material_amount)
        instance.invoice_other_costs_amount = validated_data.get('invoice_other_costs_amount', instance.invoice_other_costs_amount)
        instance.invoice_quoted_labour_amount = validated_data.get('invoice_quoted_labour_amount', instance.invoice_quoted_labour_amount)
        instance.invoice_quoted_material_amount = validated_data.get('invoice_quoted_material_amount', instance.invoice_quoted_material_amount)
        instance.invoice_quoted_other_costs_amount = validated_data.get('invoice_quoted_other_costs_amount', instance.invoice_quoted_other_costs_amount)
        instance.invoice_total_quote_amount = validated_data.get('invoice_total_quote_amount', instance.invoice_total_quote_amount)
        instance.invoice_sub_total_amount = validated_data.get('invoice_labour_amount', instance.invoice_labour_amount) + validated_data.get('invoice_material_amount', instance.invoice_material_amount) + validated_data.get('invoice_other_costs_amount', instance.invoice_other_costs_amount)
        instance.invoice_tax_amount = validated_data.get('invoice_tax_amount', instance.invoice_tax_amount)
        instance.invoice_total_amount = validated_data.get('invoice_total_amount', instance.invoice_total_amount)
        instance.invoice_deposit_amount = validated_data.get('invoice_deposit_amount', instance.invoice_deposit_amount)
        instance.invoice_amount_due = validated_data.get('invoice_amount_due', instance.invoice_amount_due)
        instance.invoice_service_fee_amount = validated_data.get('invoice_service_fee_amount', instance.invoice_service_fee_amount)
        instance.invoice_actual_service_fee_amount_paid = validated_data.get('invoice_actual_service_fee_amount_paid', instance.invoice_actual_service_fee_amount_paid)
        instance.state = validated_data.get('state', instance.state)
        instance.invoice_balance_owing_amount = validated_data.get('invoice_balance_owing_amount', instance.invoice_balance_owing_amount)
        instance.visits = validated_data.get('visits', instance.visits)
        instance.completion_date = validated_data.get('completion_date', instance.completion_date)
        instance.last_modified_by_id = user_id
        instance.last_modified_from = from_ip
        instance.last_modified_from_is_public = from_ip_is_public
        instance.save()
        logger.info("Updated order object.")

        # Run the command which will process more advanced fields pertaining to
        # the process.
        from_ip_is_public = 1 if from_ip_is_public == True else 0
        call_command('process_paid_order', tenant.schema_name, instance.id, user_id, from_ip, from_ip_is_public, verbosity=0)

        return instance
