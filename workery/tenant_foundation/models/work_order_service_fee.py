# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.constants import TASK_ITEM_TYPE_OF_CHOICES
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class WorkOrderServiceFeeManager(models.Manager):
    def delete_all(self):
        items = WorkOrderServiceFee.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def get_todays_date(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


@transaction.atomic
def increment_order_service_fee_id_number():
    """Function will generate a unique big-int."""
    last_order_service_fee = WorkOrderServiceFee.objects.all().order_by('id').last();
    if last_order_service_fee:
        return last_order_service_fee.id + 1
    return 1


class WorkOrderServiceFee(models.Model):
    """
    The percentage that must be applied on the job's total cost for the
    `Franchise` to collect as a service fee to run the organization.
    """

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_work_order_service_fees'
        ordering = ['percentage']
        verbose_name = _('Work Order Service Fee')
        verbose_name_plural = _('Work Order Service Fees')
        default_permissions = ()
        permissions = (
            ("can_get_order_service_fees", "Can get work order service fees"),
            ("can_get_order_service_fee", "Can get work order service fee"),
            ("can_post_order_service_fee", "Can create work order service fee"),
            ("can_put_order_service_fee", "Can update work order service fee"),
            ("can_delete_order_service_fee", "Can delete work order service fee"),
        )

    objects = WorkOrderServiceFeeManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_order_service_fee_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    title = models.CharField(
        _("Title"),
        max_length=63,
        help_text=_('The official title of this service.'),
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this service fee.'),
    )
    percentage = models.FloatField(
        _("Percent"),
        help_text=_('The percent to take from job orders'),
        blank=True,
        default=0
    )

    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this order.'),
        related_name="created_work_order_fees",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this order.'),
        related_name="last_modified_work_order_fees",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.id)
