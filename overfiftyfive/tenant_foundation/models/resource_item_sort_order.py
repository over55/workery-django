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
from shared_foundation.constants import *
from tenant_foundation.utils import *


class ResourceItemSortOrderManager(models.Manager):
    def delete_all(self):
        items = ResourceItemSortOrder.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_resource_item_sort_order_id_number():
    """Function will generate a unique big-int."""
    last_resource_item = ResourceItemSortOrder.objects.all().order_by('id').last();
    if last_resource_item:
        return last_resource_item.id + 1
    return 1


class ResourceItemSortOrder(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_resource_item_sort_orders'
        verbose_name = _('Resource Item Sort Order')
        verbose_name_plural = _('Resource Item Sort Orders')
        default_permissions = ()
        permissions = (
            ("can_get_resource_item_sort_orders", "Can get resource item sort orders"),
            ("can_get_resource_item_sort_order", "Can get resource item sort order"),
            ("can_post_resource_item_sort_order", "Can create resource item sort order"),
            ("can_put_resource_item_sort_order", "Can update resource item sort order"),
            ("can_delete_resource_item_sort_order", "Can delete resource item sort order"),
        )

    objects = ResourceItemSortOrderManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_resource_item_sort_order_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    category = models.ForeignKey(
        "ResourceCategory",
        help_text=_('The resource category this item belongs to.'),
        related_name="%(app_label)s_%(class)s_resource_categories",
        on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        "ResourceItem",
        help_text=_('The resource item this object belongs to.'),
        related_name="%(app_label)s_%(class)s_resource_items",
        on_delete=models.CASCADE,
    )
    ordering_number = models.PositiveSmallIntegerField(
        _("Ordering Number"),
        help_text=_('The ordering number this item will be placed per category.'),
        default=1,
        blank=True,
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.title)
