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

from shared_foundation.constants import *
from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import CUSTOMER_GROUP_ID, WORKERY_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.models import WorkOrder, WorkOrderDeposit, WorkOrderComment, Comment


logger = logging.getLogger(__name__)


class WorkOrderDepositRetrieveDeleteSerializer(serializers.ModelSerializer):
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

    def delete(self):
        #---------------------------------------
        # Lookup the deposit.
        #---------------------------------------
        the_deposit = self.context['deposit']

        #---------------------------------------
        # Calculate the new deposit amount.
        #---------------------------------------
        deposits = WorkOrderDeposit.objects.filter(order=the_deposit.order)
        amount = 0
        for deposit in deposits.all():
            if deposit is not the_deposit:
                amount += deposit.amount.amount

        the_deposit.invoice_deposit_amount = Money(amount, WORKERY_APP_DEFAULT_MONEY_CURRENCY)
        the_deposit.order.invoice_amount_due = the_deposit.order.invoice_total_amount - the_deposit.amount
        the_deposit.last_modified_by = self.context['created_by']
        the_deposit.last_modified_from = self.context['created_from']
        the_deposit.last_modified_from_is_public = self.context['created_from_is_public']
        the_deposit.save()
        logger.info("Re-calculated the amount due.")

        #---------------------------------------
        # Create a comment with special text.
        #---------------------------------------
        # [user] DELETED a payment of [$paymentamount] on [date] at [time]
        comment_text = str(self.context['created_by'])+" DELETED a payment of $" + str(the_deposit.amount.amount) + " on " + str(self.context['franchise'].get_todays_date_plus_days())
        comment = Comment.objects.create(
            created_by=self.context['created_by'],
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
            last_modified_by=self.context['created_by'],
            last_modified_from = self.context['created_from'],
            last_modified_from_is_public = self.context['created_from_is_public'],
            text=comment_text,
        )
        WorkOrderComment.objects.create(
            about=the_deposit.order,
            comment=comment,
        )
        logger.info("Attached comment to order.")

        #---------------------------------------
        # Lookup the deposit.
        #---------------------------------------
        the_deposit.delete()
        logger.info("Deleted payment")

        return self
