# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
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


class TagManager(models.Manager):
    def delete_all(self):
        items = Tag.objects.all()
        for item in items.all():
            item.delete()


class Tag(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_tags'
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        default_permissions = ()
        permissions = (
            ("can_get_tags", "Can get tags"),
            ("can_get_tag", "Can get tag"),
            ("can_post_tag", "Can create tag"),
            ("can_put_tag", "Can update tag"),
            ("can_delete_tag", "Can delete tag"),
        )

    objects = TagManager()

    #
    #  FIELDS
    #

    text = models.CharField(
        _("Text"),
        max_length=31,
        help_text=_('The text content of this tag.'),
        db_index=True,
        unique=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.text)
