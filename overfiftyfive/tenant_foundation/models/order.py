# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from tenant_foundation.models import AbstractBigPk
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class OrderManager(models.Manager):
    def delete_all(self):
        items = Order.objects.all()
        for item in items.all():
            item.delete()


class Order(AbstractBigPk):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_orders'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    objects = OrderManager()

    #
    #  FIELDS
    #

    customer = models.ForeignKey(
        "Customer",
        help_text=_('The customer of our order.'),
        related_name="%(app_label)s_%(class)s_customer_related",
        on_delete=models.CASCADE
    )
    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our order.'),
        related_name="%(app_label)s_%(class)s_associate_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    assignment_date = models.DateField(
        _('Assignment Date'),
        help_text=_('The date that an associate was assigned to the customer.'),
        blank=True,
        null=True
    )
    category_tags = models.ManyToManyField(
        "Tag",
        help_text=_('The category tags that this order belongs to.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_category_tags_related",
    )
    is_ongoing = models.BooleanField(
        _("Is Active"),
        help_text=_('Track whether this order is ongoing.'),
        default=False,
        blank=True
    )
    is_cancelled = models.BooleanField(
        _("Is Cancelled"),
        help_text=_('Track whether this order was cancelled.'),
        default=False,
        blank=True
    )
    completion_date = models.DateField(
        _('Completion Date'),
        help_text=_('The date that this order was completed.'),
        blank=True,
        null=True
    )
    hours = models.PositiveSmallIntegerField(
        _("Hours"),
        help_text=_('The total amount of hours worked on for this order by the associate.'),
        default=0
    )
    service_fee = MoneyField(
        _("Service Fee"),
        help_text=_('The service fee that the customer was charged by the associate..'),
        max_digits=10,
        decimal_places=2,
        default_currency='CAD',
        default=Money(0,'CAD'),
        blank=True,
    )
    payment_date = models.DateField(
        _('Payment Date'),
        help_text=_('The date that this order was paid for.'),
        blank=True,
        null=True
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments of this order sorted by latest creation date..'),
        blank=True,
        related_name="%(app_label)s_%(class)s_comments_related",
        through="OrderComment",
    )
    #Workmanship
    #Time / Budget
    #Punctual
    #Professional
    #Refer
    #Score

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.pk)
