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
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.models import SharedUser
from shared_foundation.constants import *
from tenant_foundation.utils import *


class ActivitySheetManager(models.Manager):
    def delete_all(self):
        items = ActivitySheet.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_activity_sheet_item_id_number():
    """Function will generate a unique big-int."""
    last_resource_item = ActivitySheet.objects.all().order_by('id').last();
    if last_resource_item:
        return last_resource_item.id + 1
    return 1


class ActivitySheetItem(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_activity_sheet_items'
        verbose_name = _('Activity Sheet Item')
        verbose_name_plural = _('Activity Sheet Items')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = (
            ("can_get_activity_sheet_items", "Can get activity sheets"),
            ("can_get_activity_sheet_item", "Can get activity sheet"),
            ("can_post_activity_sheet_item", "Can create activity sheet"),
            ("can_put_activity_sheet_item", "Can update activity sheet"),
            ("can_delete_activity_sheet_item", "Can delete activity sheet"),
        )

    objects = ActivitySheetManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_activity_sheet_item_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    order = models.ForeignKey(
        "Order",
        help_text=_('The order associated with thie activity sheet.'),
        related_name="%(app_label)s_%(class)s_orders_related",
        on_delete=models.CASCADE,
    )
    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate with this activity sheet.'),
        related_name="%(app_label)s_%(class)s_associate_related",
        on_delete=models.CASCADE,
    )
    comment = models.TextField(
        _("Comment"),
        help_text=_('A comment associated with this activity sheet item.'),
        blank=True,
        null=True,
        default='',
    )
    has_accepted_job = models.BooleanField(
        _("Has Accepted Job"),
        help_text=_('Indicates whether associate has accepted or rejected this job offer.'),
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this activity sheet.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.order)+" "+str(self.associate)+" - "+str(self.id)
