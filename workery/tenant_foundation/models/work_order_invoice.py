# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import EmailValidator
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from shared_foundation.constants import WORKERY_APP_DEFAULT_MONEY_CURRENCY
from tenant_foundation.utils import *


# Override the validator to have our custom message.
email_validator = EmailValidator(message=_("Invalid email"))


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class WorkOrderInvoiceManager(models.Manager):
    def delete_all(self):
        items = WorkOrderInvoice.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


@transaction.atomic
def increment_order_invoice_id_number():
    """Function will generate a unique big-int."""
    last_order_invoice = WorkOrderInvoice.objects.all().order_by('id').last();
    if last_order_invoice:
        return last_order_invoice.id + 1
    return 1


class WorkOrderInvoice(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_work_order_invoices'
        # ordering = ['percentage']
        verbose_name = _('Work Order Invoice')
        verbose_name_plural = _('Work Order Invoices')
        default_permissions = ()
        permissions = (
            ("can_get_order_invoices", "Can get work order invoices"),
            ("can_get_order_invoice", "Can get work order invoice"),
            ("can_post_order_invoice", "Can create work order invoice"),
            ("can_put_order_invoice", "Can update work order invoice"),
            ("can_delete_order_invoice", "Can delete work order invoice"),
        )

    objects = WorkOrderInvoiceManager()

    #
    #  OPERATION FIELDS
    #

    order = models.OneToOneField(
        "WorkOrder",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="invoice"
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether invoice was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    #
    # REQUIRED PDF FIELDS
    #

    invoice_id = models.BigIntegerField(
        _("Invoice ID"),
        help_text=_('Indicates what invoice ID is referenced on the document.'),
        blank=True,
        null=True,
    )
    invoice_date = models.DateField(
        _('Invoice Date'),
        help_text=_('The date that this invoice document was issued.'),
        blank=True,
        null=True
    )
    associate_name = models.CharField(
        _("Associate Name"),
        help_text=_('The name of the associate on this invoice document.'),
        max_length=26,
        blank=True,
        null=True,
    )
    associate_telephone = PhoneNumberField(
        _("Associate Telephone"),
        help_text=_('The associate\'s telephone number on this invoice document.'),
        blank=True,
        null=True,
    )
    client_name = models.CharField(
        _("Client Name"),
        help_text=_('The name of the client on this invoice document.'),
        max_length=63,
        blank=True,
        null=True,
    )
    client_telephone = PhoneNumberField(
        _("Client Telephone"),
        help_text=_('The client\'s telephone number on this invoice document.'),
        blank=True,
        null=True,
    )
    client_email = models.EmailField(
        _("Client Email"),
        help_text=_('The client\'s email on this invoice document.'),
        null=True,
        blank=True,
        validators=[email_validator],
        db_index=True
    )

    # LINE 1 OF 15
    line_01_qty = models.PositiveSmallIntegerField(
        _("Line 01 Quantity"),
        help_text=_('Line 01 quantity value.'),
        blank=True,
        null=True,
    )
    line_01_desc = models.CharField(
        _("Line 01 Description"),
        help_text=_('Line 01 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_01_price = MoneyField(
        _("Line 01 Price"),
        help_text=_('Line 01 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_01_amount = MoneyField(
        _("Line 01 Amount"),
        help_text=_('Line 01 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 2 OF 15
    line_02_qty = models.PositiveSmallIntegerField(
        _("Line 02 Quantity"),
        help_text=_('Line 02 quantity value.'),
        blank=True,
        null=True,
    )
    line_02_desc = models.CharField(
        _("Line 02 Description"),
        help_text=_('Line 02 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_02_price = MoneyField(
        _("Line 02 Price"),
        help_text=_('Line 02 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_02_amount = MoneyField(
        _("Line 02 Amount"),
        help_text=_('Line 02 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 3 OF 15
    line_03_qty = models.PositiveSmallIntegerField(
        _("Line 03 Quantity"),
        help_text=_('Line 03 quantity value.'),
        blank=True,
        null=True,
    )
    line_03_desc = models.CharField(
        _("Line 03 Description"),
        help_text=_('Line 03 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_03_price = MoneyField(
        _("Line 03 Price"),
        help_text=_('Line 03 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_03_amount = MoneyField(
        _("Line 03 Amount"),
        help_text=_('Line 03 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 4 OF 15
    line_04_qty = models.PositiveSmallIntegerField(
        _("Line 04 Quantity"),
        help_text=_('Line 04 quantity value.'),
        blank=True,
        null=True,
    )
    line_04_desc = models.CharField(
        _("Line 04 Description"),
        help_text=_('Line 04 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_04_price = MoneyField(
        _("Line 04 Price"),
        help_text=_('Line 04 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_04_amount = MoneyField(
        _("Line 04 Amount"),
        help_text=_('Line 04 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 5 OF 15
    line_05_qty = models.PositiveSmallIntegerField(
        _("Line 05 Quantity"),
        help_text=_('Line 05 quantity value.'),
        blank=True,
        null=True,
    )
    line_05_desc = models.CharField(
        _("Line 05 Description"),
        help_text=_('Line 05 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_05_price = MoneyField(
        _("Line 05 Price"),
        help_text=_('Line 05 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_05_amount = MoneyField(
        _("Line 05 Amount"),
        help_text=_('Line 05 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 6 OF 15
    line_06_qty = models.PositiveSmallIntegerField(
        _("Line 06 Quantity"),
        help_text=_('Line 06 quantity value.'),
        blank=True,
        null=True,
    )
    line_06_desc = models.CharField(
        _("Line 06 Description"),
        help_text=_('Line 06 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_06_price = MoneyField(
        _("Line 06 Price"),
        help_text=_('Line 06 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_06_amount = MoneyField(
        _("Line 06 Amount"),
        help_text=_('Line 06 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 07 OF 15
    line_07_qty = models.PositiveSmallIntegerField(
        _("Line 07 Quantity"),
        help_text=_('Line 07 quantity value.'),
        blank=True,
        null=True,
    )
    line_07_desc = models.CharField(
        _("Line 07 Description"),
        help_text=_('Line 07 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_07_price = MoneyField(
        _("Line 07 Price"),
        help_text=_('Line 07 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_07_amount = MoneyField(
        _("Line 07 Amount"),
        help_text=_('Line 07 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 08 OF 15
    line_08_qty = models.PositiveSmallIntegerField(
        _("Line 08 Quantity"),
        help_text=_('Line 08 quantity value.'),
        blank=True,
        null=True,
    )
    line_08_desc = models.CharField(
        _("Line 08 Description"),
        help_text=_('Line 08 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_08_price = MoneyField(
        _("Line 08 Price"),
        help_text=_('Line 08 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_08_amount = MoneyField(
        _("Line 08 Amount"),
        help_text=_('Line 08 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 09 OF 15
    line_09_qty = models.PositiveSmallIntegerField(
        _("Line 09 Quantity"),
        help_text=_('Line 09 quantity value.'),
        blank=True,
        null=True,
    )
    line_09_desc = models.CharField(
        _("Line 09 Description"),
        help_text=_('Line 09 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_09_price = MoneyField(
        _("Line 09 Price"),
        help_text=_('Line 09 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_09_amount = MoneyField(
        _("Line 09 Amount"),
        help_text=_('Line 09 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 10 OF 15
    line_10_qty = models.PositiveSmallIntegerField(
        _("Line 10 Quantity"),
        help_text=_('Line 10 quantity value.'),
        blank=True,
        null=True,
    )
    line_10_desc = models.CharField(
        _("Line 10 Description"),
        help_text=_('Line 10 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_10_price = MoneyField(
        _("Line 10 Price"),
        help_text=_('Line 10 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_10_amount = MoneyField(
        _("Line 10 Amount"),
        help_text=_('Line 10 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 11 OF 15
    line_11_qty = models.PositiveSmallIntegerField(
        _("Line 11 Quantity"),
        help_text=_('Line 11 quantity value.'),
        blank=True,
        null=True,
    )
    line_11_desc = models.CharField(
        _("Line 11 Description"),
        help_text=_('Line 11 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_11_price = MoneyField(
        _("Line 11 Price"),
        help_text=_('Line 11 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_11_amount = MoneyField(
        _("Line 11 Amount"),
        help_text=_('Line 11 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 12 OF 15
    line_12_qty = models.PositiveSmallIntegerField(
        _("Line 12 Quantity"),
        help_text=_('Line 12 quantity value.'),
        blank=True,
        null=True,
    )
    line_12_desc = models.CharField(
        _("Line 12 Description"),
        help_text=_('Line 12 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_12_price = MoneyField(
        _("Line 12 Price"),
        help_text=_('Line 12 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_12_amount = MoneyField(
        _("Line 12 Amount"),
        help_text=_('Line 12 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 13 OF 15
    line_13_qty = models.PositiveSmallIntegerField(
        _("Line 13 Quantity"),
        help_text=_('Line 13 quantity value.'),
        blank=True,
        null=True,
    )
    line_13_desc = models.CharField(
        _("Line 13 Description"),
        help_text=_('Line 13 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_13_price = MoneyField(
        _("Line 13 Price"),
        help_text=_('Line 13 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_13_amount = MoneyField(
        _("Line 13 Amount"),
        help_text=_('Line 13 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 14 OF 15
    line_14_qty = models.PositiveSmallIntegerField(
        _("Line 14 Quantity"),
        help_text=_('Line 14 quantity value.'),
        blank=True,
        null=True,
    )
    line_14_desc = models.CharField(
        _("Line 14 Description"),
        help_text=_('Line 14 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_14_price = MoneyField(
        _("Line 14 Price"),
        help_text=_('Line 14 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_14_amount = MoneyField(
        _("Line 14 Amount"),
        help_text=_('Line 14 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    # LINE 15 OF 15
    line_15_qty = models.PositiveSmallIntegerField(
        _("Line 15 Quantity"),
        help_text=_('Line 15 quantity value.'),
        blank=True,
        null=True,
    )
    line_15_desc = models.CharField(
        _("Line 15 Description"),
        help_text=_('Line 15 quantity value.'),
        max_length=45,
        blank=True,
        null=True,
    )
    line_15_price = MoneyField(
        _("Line 15 Price"),
        help_text=_('Line 15 price value per quantity.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    line_15_amount = MoneyField(
        _("Line 15 Amount"),
        help_text=_('Line 15 amount value.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )

    invoice_quote_days = models.PositiveSmallIntegerField(
        _("Invoice Quote Days"),
        help_text=_('The quote is valid for value.'),
        blank=True,
        null=True,
    )
    invoice_associate_tax = models.CharField(
        _("Invoice Associate Tax #"),
        help_text=_('The associate tax number for this invoice document.'),
        max_length=15,
        blank=True,
        null=True,
    )
    invoice_quote_date = models.DateField(
        _('Invoice Quote Date'),
        help_text=_('The date of invoice quote approval.'),
        blank=True,
        null=True
    )
    invoice_customers_approval = models.CharField(
        _("Invoice Customer Approval"),
        help_text=_('The customer approval for this invoice document.'),
        max_length=20,
        blank=True,
        null=True,
    )
    line_01_notes = models.CharField(
        _("Line 01 Notes"),
        help_text=_('The line 01 notes.'),
        max_length=80,
        blank=True,
        null=True,
    )
    line_02_notes = models.CharField(
        _("Line 01 Notes"),
        help_text=_('The line 01 notes.'),
        max_length=40,
        blank=True,
        null=True,
    )
    total_labour = MoneyField(
        _("Total Labour"),
        help_text=_('Total Labour'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    total_materials = MoneyField(
        _("Total Materials"),
        help_text=_('Total Materials'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    waste_removal = MoneyField(
        _("Waste Removal"),
        help_text=_('Waste Removal'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    sub_total = MoneyField(
        _("Sub Total"),
        help_text=_('Sub Total'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    tax = MoneyField(
        _("Tax"),
        help_text=_('Tax'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    total = MoneyField(
        _("Total"),
        help_text=_('Total'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    grand_total = MoneyField(
        _("Grand Total"),
        help_text=_('Grand Total'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    payment_amount = MoneyField(
        _("Payment Amount"),
        help_text=_('Payment Amount'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    payment_date = models.DateField(
        _('Payment Date'),
        help_text=_('The payment date for this invoice document.'),
        blank=True,
        null=True
    )
    is_cash = models.BooleanField(
        _("Is Cash"),
        help_text=_('Indicates whether cash was used or not.'),
        default=False,
        blank=True,
    )
    is_cheque = models.BooleanField(
        _("Is Cheque"),
        help_text=_('Indicates whether cheque was used or not.'),
        default=False,
        blank=True,
    )
    is_debit = models.BooleanField(
        _("Is Debit"),
        help_text=_('Indicates whether debit was used or not.'),
        default=False,
        blank=True,
    )
    is_credit = models.BooleanField(
        _("Is Credit"),
        help_text=_('Indicates whether credit was used or not.'),
        default=False,
        blank=True,
    )
    is_other = models.BooleanField(
        _("Is other"),
        help_text=_('Indicates whether other was used or not.'),
        default=False,
        blank=True,
    )
    client_signature = models.CharField(
        _("Client Signature"),
        help_text=_('Client signature.'),
        max_length=47,
        blank=True,
        null=True,
    )
    associate_sign_date = models.DateField(
        _('Associate Sign Date'),
        help_text=_('Associate Sign Date'),
        blank=True,
        null=True
    )
    associate_signature = models.CharField(
        _("Associate Signature"),
        help_text=_('Associate signature.'),
        max_length=29,
        blank=True,
        null=True,
    )
    work_order_id = models.BigIntegerField(
        _("Work Order ID"),
        help_text=_('Work order ID'),
        blank=True,
        null=True,
    )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="created_work_order_invoices",
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
        related_name="last_modified_work_order_invoices",
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
        return str(self.order)
