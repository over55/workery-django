# -*- coding: utf-8 -*-
import csv
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from django.conf import settings
from django.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
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
from shared_foundation.constants import O55_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import UNASSIGNED_JOB_TYPE_OF_ID, JOB_TYPE_OF_CHOICES
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class OrderManager(models.Manager):
    def delete_all(self):
        items = Order.objects.all()
        for item in items.all():
            item.delete()

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return Order.objects.annotate(search=SearchVector(
            'customer__email',
            'customer__telephone',
            'customer__other_telephone',
            'customer__given_name',
            'customer__middle_name',
            'customer__last_name',
            'associate__email',
            'associate__telephone',
            'associate__other_telephone',
            'associate__given_name',
            'associate__middle_name',
            'associate__last_name',
        ),).filter(search=keyword)


@transaction.atomic
def increment_order_id_number():
    """Function will generate a unique big-int."""
    last_job_order = Order.objects.all().order_by('id').last();
    if last_job_order:
        return last_job_order.id + 1
    return 1


class Order(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_orders'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        default_permissions = ()
        permissions = (
            ("can_get_orders", "Can get orders"),
            ("can_get_order", "Can get order"),
            ("can_post_order", "Can create order"),
            ("can_put_order", "Can update order"),
            ("can_delete_order", "Can delete order"),
        )

    objects = OrderManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_order_id_number,
       editable=False,
       db_index=True
    )

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
    description = models.TextField(
        _("Description"),
        help_text=_('A description of this job.'),
        blank=True,
        null=True,
        default='',
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
        _("Is ongoing"),
        help_text=_('Track whether this order is ongoing job or one-time job.'),
        default=False,
        blank=True
    )
    is_home_support_service = models.BooleanField(
        _("Is Home Support Service"),
        help_text=_('Track whether this order is a home support service request.'),
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
        default_currency=O55_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,O55_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    payment_date = models.DateField(
        _('Payment Date'),
        help_text=_('The date that this order was paid for.'),
        blank=True,
        null=True
    )
    skill_sets = models.ManyToManyField(
        "SkillSet",
        help_text=_('The skill sets that belong to this order.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_skill_sets_related",
    )
    #Workmanship
    #Time / Budget
    #Punctual
    #Professional
    #Refer
    #Score
    type_of = models.PositiveSmallIntegerField(
        _("Type Of"),
        help_text=_('The type of job this is.'),
        default=UNASSIGNED_JOB_TYPE_OF_ID,
        choices=JOB_TYPE_OF_CHOICES,
        blank=True,
    )

    #
    #  SYSTEM
    #
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this order.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.pk)
