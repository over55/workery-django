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
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class ResourceItemManager(models.Manager):
    def delete_all(self):
        items = ResourceItem.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_resource_item_id_number():
    """Function will generate a unique big-int."""
    last_resource_item = ResourceItem.objects.all().order_by('id').last();
    if last_resource_item:
        return last_resource_item.id + 1
    return 1


class ResourceItem(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_resource_items'
        verbose_name = _('Resource Item')
        verbose_name_plural = _('Resource Items')
        default_permissions = ()
        permissions = (
            ("can_get_resource_items", "Can get resource_items"),
            ("can_get_resource_item", "Can get resource_item"),
            ("can_post_resource_item", "Can create resource_item"),
            ("can_put_resource_item", "Can update resource_item"),
            ("can_delete_resource_item", "Can delete resource_item"),
        )

    objects = ResourceItemManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_resource_item_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    icon = models.CharField(
        _("icon"),
        max_length=31,
        help_text=_('The icon of this resource item.'),
        db_index=True,
        blank=True
    )
    title = models.CharField(
        _("title"),
        max_length=63,
        help_text=_('The title of this resource item.'),
        db_index=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this resource item.'),
        blank=True,
        null=True,
        default='',
    )
    category = models.ForeignKey(
        "ResourceCategory",
        help_text=_('The resource category this item belongs to.'),
        related_name="%(app_label)s_%(class)s_resource_categories",
        on_delete=models.CASCADE,
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.title)
