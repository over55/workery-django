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


class HowHearAboutUsItemManager(models.Manager):
    def delete_all(self):
        items = HowHearAboutUsItem.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_tag_id_number():
    """Function will generate a unique big-int."""
    last_tag = HowHearAboutUsItem.objects.all().order_by('id').last();
    if last_tag:
        return last_tag.id + 1
    return 1


class HowHearAboutUsItem(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_how_hear_about_us_items'
        verbose_name = _('How Hear About Us Item')
        verbose_name_plural = _('How Hear About Us Items')
        default_permissions = ()
        permissions = (
            ("can_get_tags", "Can get tags"),
            ("can_get_tag", "Can get tag"),
            ("can_post_tag", "Can create tag"),
            ("can_put_tag", "Can update tag"),
            ("can_delete_tag", "Can delete tag"),
        )

    objects = HowHearAboutUsItemManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_tag_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    text = models.CharField(
        _("Text"),
        max_length=127,
        help_text=_('The text content of this item.'),
        db_index=True,
        unique=True
    )
    sort_number = models.PositiveSmallIntegerField(
        _("Sort #"),
        help_text=_('The number this item will appear when sorted by number.'),
        blank=True,
        default=0,
        db_index=True,
    )
    is_for_associate = models.BooleanField(
        _("Is for associate"),
        help_text=_('Indicates this option will be visible for the associate.'),
        default=True,
        blank=True
    )
    is_for_customer = models.BooleanField(
        _("Is for customer"),
        help_text=_('Indicates this option will be visible for the customer.'),
        default=True,
        blank=True
    )
    is_for_staff = models.BooleanField(
        _("Is for staff"),
        help_text=_('Indicates this option will be visible for the staff.'),
        default=True,
        blank=True
    )
    is_for_partner = models.BooleanField(
        _("Is for partner"),
        help_text=_('Indicates this option will be visible for the partner.'),
        default=True,
        blank=True
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether how hear item was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.text)
