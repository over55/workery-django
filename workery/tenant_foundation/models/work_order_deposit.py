# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import WORKERY_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import TASK_ITEM_TYPE_OF_CHOICES, WORK_ORDER_PAID_TO_CHOICES
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class WorkOrderDepositManager(models.Manager):
    def delete_all(self):
        items = WorkOrderDeposit.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


@transaction.atomic
def increment_order_deposit_id_number():
    """Function will generate a unique big-int."""
    last_order_deposit = WorkOrderDeposit.objects.all().order_by('id').last();
    if last_order_deposit:
        return last_order_deposit.id + 1
    return 1


class WorkOrderDeposit(models.Model):

    '''
    METADATA
    '''

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_work_order_deposits'
        verbose_name = _('Work Order Deposit')
        verbose_name_plural = _('Work Order Deposits')
        default_permissions = ()
        permissions = (
            ("can_get_order_deposits", "Can get work order deposits"),
            ("can_get_order_deposit", "Can get work order deposit"),
            ("can_post_order_deposit", "Can create work order deposit"),
            ("can_put_order_deposit", "Can update work order deposit"),
            ("can_delete_order_deposit", "Can delete work order deposit"),
        )

    '''
    CONSTANTS
    '''

    class DEPOSIT_METHOD:
        CASH = 1
        CHEQUE = 2
        CREDIT = 3
        DEBIT = 4

    class DEPOSIT_FOR:
        LABOUR = 1
        MATERIALS = 2
        WASTE_REMOVAL = 3
        AMOUNT_DUE = 4

    '''
    CHOICES
    '''

    DEPOSIT_METHOD_CHOICES = (
        (DEPOSIT_METHOD.CASH, _('Cash')),
        (DEPOSIT_METHOD.CHEQUE, _('Cheque')),
        (DEPOSIT_METHOD.CREDIT, _('Credit')),
        (DEPOSIT_METHOD.DEBIT, _('Debit')),
    )

    DEPOSIT_FOR_CHOICES = (
        (DEPOSIT_FOR.LABOUR, _('Labour')),
        (DEPOSIT_FOR.MATERIALS, _('Materials')),
        (DEPOSIT_FOR.WASTE_REMOVAL, _('Waste Removal')),
        (DEPOSIT_FOR.AMOUNT_DUE, _('Amount Due')),
    )

    '''
    OBJECT MANAGERS
    '''

    objects = WorkOrderDepositManager()

    '''
    MODEL FIELDS
    '''

    id = models.BigAutoField(
       primary_key=True,
       default=increment_order_deposit_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    order = models.ForeignKey(
        "WorkOrder",
        help_text=_('The order whom this deposit belongs to.'),
        related_name="work_order_deposits",
        on_delete=models.CASCADE,
    )
    paid_at = models.DateField(
        _("Paid at"),
        help_text=_('The date this deposit was paid.'),
        null=True,
        blank=True,
    )
    deposit_method = models.PositiveSmallIntegerField(
        _("Deposit Method"),
        help_text=_('The method used for this deposit'),
        choices=DEPOSIT_METHOD_CHOICES
    )
    paid_to = models.PositiveSmallIntegerField(
        _("Paid to"),
        help_text=_('Whom was paid by the client for this invoice.'),
        choices=WORK_ORDER_PAID_TO_CHOICES,
        blank=True,
        null=True,
    )
    amount = MoneyField(
        _("Amount"),
        help_text=_('The amount that was deposited.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    paid_for = models.PositiveSmallIntegerField(
        _("Paid for"),
        help_text=_('What was this deposit for?'),
        choices=DEPOSIT_FOR_CHOICES,
        blank=True
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether deposit was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="created_work_order_deposits",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this order.'),
        related_name="last_modified_work_order_deposits",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.id)

    def get_pretty_deposit_method(self):
        return str(dict(self.DEPOSIT_METHOD_CHOICES).get(self.deposit_method))

    def get_pretty_paid_to(self):
        return str(dict(WORK_ORDER_PAID_TO_CHOICES).get(self.paid_to))

    def get_pretty_paid_for(self):
        return str(dict(self.DEPOSIT_FOR_CHOICES).get(self.paid_for))
