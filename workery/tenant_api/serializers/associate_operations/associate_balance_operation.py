# -*- coding: utf-8 -*-
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

from shared_foundation.custom.drf.fields import PhoneNumberField, GenericFileBase64File
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_content_file_from_base64_string
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Associate,
    WorkOrder,
    WORK_ORDER_STATE
)


class WorkOrderFinancialListSerializer(serializers.ModelSerializer):
    type_of = serializers.SerializerMethodField()
    completion_date = serializers.DateField(read_only=True)
    pretty_state = serializers.ReadOnlyField(source='get_pretty_status')
    invoice_service_fee = serializers.SerializerMethodField()

    # Meta Information.
    class Meta:
        model = WorkOrder
        fields = (
            'id',
            'type_of',
            'completion_date',

            'invoice_service_fee',
            # 'invoice_ids',
            'invoice_service_fee_payment_date',
            # 'invoice_date',
            # 'invoice_quote_amount',
            'invoice_labour_amount',
            # 'invoice_material_amount',
            'invoice_quoted_labour_amount',
            # 'invoice_quoted_material_amount',
            # 'invoice_total_quote_amount',
            # 'invoice_tax_amount',
            # 'invoice_total_amount',
            'invoice_service_fee_amount',
            'invoice_actual_service_fee_amount_paid',
            'state',
            'pretty_state',
            'invoice_balance_owing_amount',
            # 'visits',
        )

    def get_type_of(self, obj):
        try:
            job_type_of = UNASSIGNED_JOB_TYPE_OF_ID
            if obj.customer.type_of == RESIDENTIAL_CUSTOMER_TYPE_OF_ID:
                return RESIDENTIAL_JOB_TYPE_OF_ID
            if obj.customer.type_of == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
                return COMMERCIAL_JOB_TYPE_OF_ID
            return job_type_of
        except Exception as e:
            return None

    def get_invoice_service_fee(self, obj):
        try:
            return str(obj.invoice_service_fee.title)
        except Exception as e:
            return None


class AssociateBalanceOperationSerializer(serializers.Serializer):
    count = serializers.SerializerMethodField()
    # next
    # previous
    results = serializers.SerializerMethodField()

    def get_count(self, associate):
        try:
            return associate.work_orders.all().count()
        except Exception as e:
            return 0

    def get_results(self, associate):
        try:
            orders = associate.work_orders.filter(state=WORK_ORDER_STATE.COMPLETED_AND_PAID).order_by('-invoice_service_fee_payment_date').prefetch_related(
                'invoice_service_fee',
            )
            # print("--->>>", orders)
            s = WorkOrderFinancialListSerializer(orders, many=True)
            return s.data
        except Exception as e:
            print(e)
            return []
