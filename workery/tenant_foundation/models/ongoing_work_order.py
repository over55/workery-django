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
    Class model to represent an ongoing job. This model is essentially a
    modified `WorkOrder` model tailered to work as `master form` which will
    (1) Keep track fo the job requirements
    (2) Used to re-create work orders based on the details in this `master form`.
    (3) Used to keep track of previous closed `WorkOrder` objects associated
        with this `master form`.
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
    assignment_date = models.DateField(
        _('Assignment Date'),
        help_text=_('The date that an associate was assigned to the customer.'),
        blank=True,
        null=True
    )
    start_date = models.DateField(
        _('Start Date'),
        help_text=_('The date that this ongoing order will begin.'),
        blank=True,
        default=get_todays_date
    )
    frequency = models.CharField(
        _("Frequency"),
        help_text=_('The frequency of the ongoing job.'),
        max_length=31,
        blank=True,
        null=True,
    )
    completion_date = models.DateField(
        _('Completion Date'),
        help_text=_('The date that this ongoing order was completed.'),
        blank=True,
        null=True
    )
    hours = models.DecimalField(
        _("Hours"),
        help_text=_('The total amount of hours worked on for this ongoing order by the associate.'),
        default=0,
        max_digits=7,
        decimal_places=1,
        blank=True,
        null=True
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A description of this ongoing order.'),
        blank=True,
        null=True,
        default='',
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The category tags that this order belongs to.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related",
    )
    is_home_support_service = models.BooleanField(
        _("Is Home Support Service"),
        help_text=_('Track whether this order is a home support service request.'),
        default=False,
        blank=True
    )
    skill_sets = models.ManyToManyField(
        "SkillSet",
        help_text=_('The skill sets that belong to this order.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_skill_sets_related",
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type Of"),
        help_text=_('The type of job this is.'),
        default=UNASSIGNED_JOB_TYPE_OF_ID,
        choices=JOB_TYPE_OF_CHOICES,
        blank=True,
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments belonging to this ongoing order.'),
        blank=True,
        through='OngoingWorkOrderComment',
        related_name="%(app_label)s_%(class)s_ongoing_order_comments_related"
    )

    #
    # TASK FIELDS
    #

    latest_pending_task = models.ForeignKey(
        "TaskItem",
        help_text=_('The latest pending task of our ongoing job order.'),
        related_name="%(app_label)s_%(class)s_latest_pending_task_task_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    #
    # AGGREGATION FIELDS
    #

    closed_orders = models.ManyToManyField(
        "WorkOrder",
        help_text=_('The work orders associated with this ongoing work order.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_closed_orders_related"
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
        related_name="%(app_label)s_%(class)s_created_by_related",
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
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
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
