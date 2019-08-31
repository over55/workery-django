# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from django_fsm import FSMField, transition
from django.conf import settings
from django.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
from tenant_foundation.utils import *


class ONGOING_WORK_ORDER_STATE:
    IDLE = 'idle'
    RUNNING = 'running'
    TERMINATED = 'terminated'


class OngoingWorkOrderManager(models.Manager):
    def delete_all(self):
        items = OngoingWorkOrder.objects.all()
        for item in items.all():
            item.delete()

@transaction.atomic
def increment_order_id_number():
    """Function will generate a unique big-int."""
    last_job_order = OngoingWorkOrder.objects.all().order_by('id').last();
    if last_job_order:
        return last_job_order.id + 1
    return 1


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class OngoingWorkOrder(models.Model):
    """
    Class model to represent an ongoing job. This model is essentially a
    `master form` which will:
    (1)
    """
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_ongoing_work_orders'
        verbose_name = _('Ongoing Work Order')
        verbose_name_plural = _('Ongoing Work Orders')
        default_permissions = ()
        permissions = (
            ("can_get_orders", "Can get work orders"),
            ("can_get_order", "Can get work order"),
            ("can_post_order", "Can create work order"),
            ("can_put_order", "Can update work order"),
            ("can_delete_order", "Can delete work order"),
        )

    objects = OngoingWorkOrderManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_order_id_number,
       editable=False,
       db_index=True
    )

    #
    #  WORK ORDER FIELDS
    #

    customer = models.ForeignKey(
        "Customer",
        help_text=_('The customer of our ongoing work order.'),
        related_name="ongoing_work_orders",
        on_delete=models.CASCADE
    )
    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our ongoing work order.'),
        related_name="ongoing_work_orders",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments belonging to this ongoing order.'),
        blank=True,
        through='OngoingWorkOrderComment',
        related_name="ongoing_work_orders"
    )

    #
    # STATE FIELDS
    #

    state = FSMField(
        _('State'),
        help_text=_('The state of this ongoing work order.'),
        default=ONGOING_WORK_ORDER_STATE.IDLE,
        blank=True,
        db_index=True,
    )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this ongoing order.'),
        related_name="created_ongoing_work_orders",
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
        help_text=_('The user whom last modified this ongoing order.'),
        related_name="last_modified_ongoing_work_orders",
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
        return str(self.pk)

    def get_pretty_status(self):
        """
        Function returns the ongoing job status in a more user-friendly format.
        """
        if self.state == ONGOING_WORK_ORDER_STATE.IDLE:
            return 'Idle'
        if self.state == ONGOING_WORK_ORDER_STATE.RUNNING:
            return 'Running'
        if self.state == ONGOING_WORK_ORDER_STATE.TERMINATED:
            return 'Terminated'
        return None

    def get_pretty_type_of(self):
        if self.customer.type_of == RESIDENTIAL_CUSTOMER_TYPE_OF_ID:
            return "Residential"
        elif self.customer.type_of == COMMERCIAL_CUSTOMER_TYPE_OF_ID:
            return "Commercial"
        return None
