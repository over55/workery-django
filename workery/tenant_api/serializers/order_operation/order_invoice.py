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
from django.utils.text import Truncator
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
    TaskItem,
    WorkOrderInvoice
)


logger = logging.getLogger(__name__)



class WorkOrderInvoiceCreateOrUpdateOperationSerializer(serializers.Serializer):
    invoice_id = serializers.CharField(required=True, write_only=True, allow_null=False, allow_blank=False,)
    invoice_date = serializers.DateField(required=True, write_only=True,)

    line01_qty = serializers.IntegerField(required=True, write_only=True,)
    line01_desc = serializers.CharField(required=True, write_only=True,)
    line01_price = serializers.FloatField(required=True, write_only=True,)
    line01_amount = serializers.FloatField(required=True, write_only=True,)
    line02_qty = serializers.IntegerField(required=False, write_only=True,)
    line02_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line02_price = serializers.FloatField(required=False, write_only=True,)
    line02_amount = serializers.FloatField(required=False, write_only=True,)
    line03_qty = serializers.IntegerField(required=False, write_only=True,)
    line03_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line03_price = serializers.FloatField(required=False, write_only=True,)
    line03_amount = serializers.FloatField(required=False, write_only=True,)
    line04_qty = serializers.IntegerField(required=False, write_only=True,)
    line04_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line04_price = serializers.FloatField(required=False, write_only=True,)
    line04_amount = serializers.FloatField(required=False, write_only=True,)
    line05_qty = serializers.IntegerField(required=False, write_only=True,)
    line05_desc = serializers.CharField(required=False, write_only=True,allow_null=True,)
    line05_price = serializers.FloatField(required=False, write_only=True,)
    line05_amount = serializers.FloatField(required=False, write_only=True,)
    line06_qty = serializers.IntegerField(required=False, write_only=True,)
    line06_desc = serializers.CharField(required=False, write_only=True,allow_null=True,)
    line06_price = serializers.FloatField(required=False, write_only=True,)
    line06_amount = serializers.FloatField(required=False, write_only=True,)
    line07_qty = serializers.IntegerField(required=False, write_only=True,)
    line07_desc = serializers.CharField(required=False, write_only=True,allow_null=True,)
    line07_price = serializers.FloatField(required=False, write_only=True,)
    line07_amount = serializers.FloatField(required=False, write_only=True,)
    line08_qty = serializers.IntegerField(required=False, write_only=True,)
    line08_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line08_price = serializers.FloatField(required=False, write_only=True,)
    line08_amount = serializers.FloatField(required=False, write_only=True,)
    line09_qty = serializers.IntegerField(required=False, write_only=True,)
    line09_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line09_price = serializers.FloatField(required=False, write_only=True,)
    line09_amount = serializers.FloatField(required=False, write_only=True,)
    line10_qty = serializers.IntegerField(required=False, write_only=True,)
    line10_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line10_price = serializers.FloatField(required=False, write_only=True,)
    line10_amount = serializers.FloatField(required=False, write_only=True,)
    line11_qty = serializers.IntegerField(required=False, write_only=True,)
    line11_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line11_price = serializers.FloatField(required=False, write_only=True,)
    line11_amount = serializers.FloatField(required=False, write_only=True,)
    line12_qty = serializers.IntegerField(required=False, write_only=True,)
    line12_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line12_price = serializers.FloatField(required=False, write_only=True,)
    line12_amount = serializers.FloatField(required=False, write_only=True,)
    line13_qty = serializers.IntegerField(required=False, write_only=True,)
    line13_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line13_price = serializers.FloatField(required=False, write_only=True,)
    line13_amount = serializers.FloatField(required=False, write_only=True,)
    line14_qty = serializers.IntegerField(required=False, write_only=True,)
    line14_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line14_price = serializers.FloatField(required=False, write_only=True,)
    line14_amount = serializers.FloatField(required=False, write_only=True,)
    line15_qty = serializers.IntegerField(required=False, write_only=True,)
    line15_desc = serializers.CharField(required=False, write_only=True, allow_null=True,)
    line15_price = serializers.FloatField(required=False, write_only=True,)
    line15_amount = serializers.FloatField(required=False, write_only=True,)
    invoice_quote_days = serializers.IntegerField(required=True, write_only=True,)
    invoice_quote_date = serializers.DateField(required=True, write_only=True,)
    invoice_customers_approval = serializers.CharField(required=True, write_only=True,)
    line01_notes = serializers.CharField(required=True, write_only=True,)
    line02_notes = serializers.CharField(required=False, write_only=True, allow_null=True, allow_blank=True,)
    payment_amount = serializers.FloatField(required=False, write_only=True,)
    payment_date = serializers.DateField(required=True, write_only=True,)
    cash = serializers.BooleanField(required=False, write_only=True,)
    cheque = serializers.BooleanField(required=False, write_only=True,)
    debit = serializers.BooleanField(required=False, write_only=True,)
    credit = serializers.BooleanField(required=False, write_only=True,)
    other = serializers.BooleanField(required=False, write_only=True,)
    client_signature = serializers.CharField(required=True, write_only=True,)
    associate_sign_date = serializers.DateField(required=True, write_only=True,)
    associate_signature = serializers.CharField(required=True, write_only=True,)
    work_order_id = serializers.IntegerField(required=True, write_only=True,)
    was_created = serializers.BooleanField(required=False, read_only=True,)

    # Meta Information.
    class Meta:
        fields = (
            'invoice_id', 'invoice_date',
            'line01_qty', ' line01_desc', 'line01_price', 'line01_amount',
            'line02_qty', ' line02_desc', 'line02_price', 'line02_amount',
            'line03_qty', ' line03_desc', 'line03_price', 'line03_amount',
            'line04_qty', ' line04_desc', 'line04_price', 'line04_amount',
            'line05_qty', ' line05_desc', 'line05_price', 'line05_amount',
            'line06_qty', ' line06_desc', 'line06_price', 'line06_amount',
            'line07_qty', ' line07_desc', 'line07_price', 'line07_amount',
            'line08_qty', ' line08_desc', 'line08_price', 'line08_amount',
            'line09_qty', ' line09_desc', 'line09_price', 'line09_amount',
            'line10_qty', ' line10_desc', 'line10_price', 'line10_amount',
            'line11_qty', ' line11_desc', 'line11_price', 'line11_amount',
            'line12_qty', ' line12_desc', 'line12_price', 'line12_amount',
            'line13_qty', ' line13_desc', 'line13_price', 'line13_amount',
            'line14_qty', ' line14_desc', 'line14_price', 'line14_amount',
            'line15_qty', ' line15_desc', 'line15_price', 'line15_amount',
            'invoice_quote_days', 'invoice_quote_date', 'invoice_customers_approval',
            'line01_notes', 'line02_notes', 'payment_amount', 'payment_date',
            'cash', 'cheque', 'debit', 'credit', 'other', 'client_signature',
            'associate_sign_date', 'associate_signature', 'work_order_id',
        )


    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #--------------------------#
        # Get validated POST data. #
        #--------------------------#
        work_order_id = validated_data.get('work_order_id', None)
        order = WorkOrder.objects.get(id=work_order_id)

        #------------------#
        # Process the data #
        #------------------#
        invoice, was_created = WorkOrderInvoice.objects.update_or_create(
            order=order,
            defaults={
                'order': order,
                'invoice_id': validated_data.get('invoice_id', None),
                'invoice_date': validated_data.get('invoice_date', None),
                'associate_name': order.associate.owner.get_full_name(),
                'associate_telephone': order.associate.telephone,
                'client_name': order.customer.get_pretty_name(),
                'client_address': order.customer.get_postal_address(),
                'client_telephone': order.customer.telephone,
                'client_email': order.customer.email,
                'line_01_qty': validated_data.get('line01_qty', None),
                'line_01_desc': Truncator(validated_data.get('line01_desc', None)).chars(45),
                'line_01_price': validated_data.get('line01_price', 0),
                'line_01_amount': validated_data.get('line01_amount', 0),
                'line_02_qty': validated_data.get('line02_qty', None),
                'line_02_desc': Truncator(validated_data.get('line02_desc', None)).chars(45),
                'line_02_price': validated_data.get('line02_price', 0),
                'line_02_amount': validated_data.get('line02_amount', 0),
                'line_03_qty': validated_data.get('line03_qty', None),
                'line_03_desc': Truncator(validated_data.get('line03_desc', None)).chars(45),
                'line_03_price': validated_data.get('line03_price', 0),
                'line_03_amount': validated_data.get('line03_amount', 0),
                'line_04_qty': validated_data.get('line04_qty', None),
                'line_04_desc': Truncator(validated_data.get('line04_desc', None)).chars(45),
                'line_04_price': validated_data.get('line04_price', 0),
                'line_04_amount': validated_data.get('line04_amount', 0),
                'line_05_qty': validated_data.get('line05_qty', None),
                'line_05_desc': Truncator(validated_data.get('line05_desc', None)).chars(45),
                'line_05_price': validated_data.get('line05_price', 0),
                'line_05_amount': validated_data.get('line05_amount', 0),
                'line_06_qty': validated_data.get('line06_qty', None),
                'line_06_desc': Truncator(validated_data.get('line06_desc', None)).chars(45),
                'line_06_price': validated_data.get('line06_price', 0),
                'line_06_amount': validated_data.get('line06_amount', 0),
                'line_07_qty': validated_data.get('line07_qty', None),
                'line_07_desc': Truncator(validated_data.get('line07_desc', None)).chars(45),
                'line_07_price': validated_data.get('line07_price', 0),
                'line_07_amount': validated_data.get('line07_amount', 0),
                'line_08_qty': validated_data.get('line08_qty', None),
                'line_08_desc': Truncator(validated_data.get('line08_desc', None)).chars(45),
                'line_08_price': validated_data.get('line08_price', 0),
                'line_08_amount': validated_data.get('line08_amount', 0),
                'line_09_qty': validated_data.get('line09_qty', None),
                'line_09_desc': Truncator(validated_data.get('line09_desc', None)).chars(45),
                'line_09_price': validated_data.get('line09_price', 0),
                'line_09_amount': validated_data.get('line09_amount', 0),
                'line_10_qty': validated_data.get('line10_qty', None),
                'line_10_desc': Truncator(validated_data.get('line10_desc', None)).chars(45),
                'line_10_price': validated_data.get('line10_price', 0),
                'line_10_amount': validated_data.get('line10_amount', 0),
                'line_11_qty': validated_data.get('line11_qty', None),
                'line_11_desc': Truncator(validated_data.get('line11_desc', None)).chars(45),
                'line_11_price': validated_data.get('line11_price', 0),
                'line_11_amount': validated_data.get('line11_amount', 0),
                'line_12_qty': validated_data.get('line12_qty', None),
                'line_12_desc': Truncator(validated_data.get('line12_desc', None)).chars(45),
                'line_12_price': validated_data.get('line12_price', 0),
                'line_12_amount': validated_data.get('line12_amount', 0),
                'line_13_qty': validated_data.get('line13_qty', None),
                'line_13_desc': Truncator(validated_data.get('line13_desc', None)).chars(45),
                'line_13_price': validated_data.get('line13_price', 0),
                'line_13_amount': validated_data.get('line13_amount', 0),
                'line_14_qty': validated_data.get('line14_qty', None),
                'line_14_desc': Truncator(validated_data.get('line14_desc', None)).chars(45),
                'line_14_price': validated_data.get('line14_price', 0),
                'line_14_amount': validated_data.get('line14_amount', 0),
                'line_15_qty': validated_data.get('line15_qty', None),
                'line_15_desc': Truncator(validated_data.get('line15_desc', None)).chars(45),
                'line_15_price': validated_data.get('line15_price', 0),
                'line_15_amount': validated_data.get('line15_amount', 0),
                'invoice_quote_days': validated_data.get('invoice_quote_days', None),
                'invoice_quote_date': validated_data.get('invoice_quote_date', None),
                'invoice_associate_tax': Truncator(order.associate.tax_id).chars(18),
                'invoice_customers_approval': validated_data.get('invoice_customers_approval', None),
                'line_01_notes': validated_data.get('line01_notes', None),
                'line_02_notes': validated_data.get('line02_notes', None),
                'total_labour': order.invoice_labour_amount,
                'total_materials': order.invoice_material_amount,
                # 'waste_removal': //TODO: IMPLEMENT
                'amount_due': order.invoice_amount_due,
                'tax': order.invoice_tax_amount,
                'total':  order.invoice_total_amount,
                'deposit': order.invoice_deposit_amount,
                'payment_amount': validated_data.get('payment_amount', 0),
                'payment_date': validated_data.get('payment_date', None),
                'is_cash': validated_data.get('cash', None),
                'is_cheque': validated_data.get('cheque', None),
                'is_debit': validated_data.get('debit', None),
                'is_credit': validated_data.get('credit', None),
                'is_other': validated_data.get('other', None),
                'client_signature': validated_data.get('client_signature', None),
                'associate_sign_date': validated_data.get('associate_sign_date', None),
                'associate_signature': validated_data.get('associate_signature', None),
                'work_order_id': work_order_id,
                'created_by': self.context['user'],
                'created_from': self.context['from'],
                'created_from_is_public': self.context['from_is_public'],
                'last_modified_by': self.context['user'],
                'last_modified_from': self.context['from'],
                'last_modified_from_is_public': self.context['from_is_public'],
            },
        )

        order.invoice = invoice
        order.last_modified_by = self.context['user']
        order.last_modified_from = self.context['from']
        order.last_modified_from_is_public = self.context['from_is_public']
        order.save()

        # raise serializers.ValidationError("ccc") # For debuggingp purposes only.

        #--------------------#
        # Updated the output #
        #--------------------#
        return order
