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
from shared_foundation.models import SharedUser
from shared_foundation.constants import *
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class BulletinBoardItemManager(models.Manager):
    def delete_all(self):
        items = BulletinBoardItem.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_bulletin_board_item_id_number():
    """Function will generate a unique big-int."""
    last_bulletin_board_item = BulletinBoardItem.objects.all().order_by('id').last();
    if last_bulletin_board_item:
        return last_bulletin_board_item.id + 1
    return 1


class BulletinBoardItem(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_bulletin_board_items'
        verbose_name = _('Bulletin Board Item')
        verbose_name_plural = _('Bulletin Board Items')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = (
            ("can_get_bulletin_board_items", "Can get bulletin board items"),
            ("can_get_bulletin_board_item", "Can get bulletin board item"),
            ("can_post_bulletin_board_item", "Can create bulletin board item"),
            ("can_put_bulletin_board_item", "Can update bulletin board item"),
            ("can_delete_bulletin_board_item", "Can delete bulletin board item"),
        )

    #
    #  SYSTEM FIELDS
    #

    objects = BulletinBoardItemManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_bulletin_board_item_id_number,
       editable=False,
       db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this away log.'),
        related_name="created_bulletin_board_itemss",
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
        help_text=_('The user whom last modified this away log.'),
        related_name="last_modified_bulletin_board_items",
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
    #  CUSTOM FIELDS
    #

    text = models.TextField(
        _("Text"),
        help_text=_('The text content of this bulletin board item.'),
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether bulletin board item was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.text)
