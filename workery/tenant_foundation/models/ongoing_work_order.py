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
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import WORKERY_APP_DEFAULT_MONEY_CURRENCY
from shared_foundation.models import SharedUser
from tenant_foundation.constants import UNASSIGNED_JOB_TYPE_OF_ID, JOB_TYPE_OF_CHOICES
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
    The model used to keep track and aggregate all `WorkOrder` objects which
    are ongoing.
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
    #  FIELDS
    #

    customer = models.ForeignKey(
        "Customer",
        help_text=_('The customer of our ongoing work order.'),
        related_name="%(app_label)s_%(class)s_customer_related",
        on_delete=models.CASCADE
    )
    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our ongoing work order.'),
        related_name="%(app_label)s_%(class)s_associate_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    latest_pending_task = models.ForeignKey(
        "TaskItem",
        help_text=_('The latest pending task of our ongoing job order.'),
        related_name="%(app_label)s_%(class)s_latest_pending_task_task_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    # DEPRECATE BELOW
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    closed_orders = models.ManyToManyField(
        "WorkOrder",
        help_text=_('The work orders associated with this ongoing work order.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_closed_orders_related"
    )
    open_order = models.ForeignKey(
        "WorkOrder",
        help_text=_('The work order which is currently running for this ongoing work order.'),
        related_name="%(app_label)s_%(class)s_open_order_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    #
    # State
    #

    state = FSMField(
        _('State'),
        help_text=_('The state of this ongoing work order.'),
        default=ONGOING_WORK_ORDER_STATE.IDLE,
        blank=True,
        db_index=True,
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.pk)
