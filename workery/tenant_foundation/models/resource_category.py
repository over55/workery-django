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


class ResourceCategoryManager(models.Manager):
    def delete_all(self):
        items = ResourceCategory.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_resource_category_id_number():
    """Function will generate a unique big-int."""
    last_resource_category = ResourceCategory.objects.all().order_by('id').last();
    if last_resource_category:
        return last_resource_category.id + 1
    return 1


class ResourceCategory(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_resource_categories'
        verbose_name = _('Resource Category')
        verbose_name_plural = _('Resource Categories')
        default_permissions = ()
        permissions = (
            ("can_get_resource_categories", "Can get resource_categories"),
            ("can_get_resource_category", "Can get resource_category"),
            ("can_post_resource_category", "Can create resource_category"),
            ("can_put_resource_category", "Can update resource_category"),
            ("can_delete_resource_category", "Can delete resource_category"),
        )

    objects = ResourceCategoryManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_resource_category_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    icon = models.CharField(
        _("icon"),
        max_length=31,
        help_text=_('The icon of this resource category.'),
        db_index=True,
        unique=True
    )
    title = models.CharField(
        _("title"),
        max_length=63,
        help_text=_('The title of this resource category.'),
        db_index=True,
        unique=True
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this resource category.'),
        blank=True,
        null=True,
        default='',
    )
    sorted_items = models.ManyToManyField(
        "ResourceItem",
        help_text=_('The items belonging to this category sorted by "ordering_number" field.'),
        blank=True,
        through='ResourceItemSortOrder'
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.title)
