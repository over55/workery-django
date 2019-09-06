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


class VehicleTypeManager(models.Manager):
    def delete_all(self):
        items = VehicleType.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_vehicle_type_id_number():
    """Function will generate a unique big-int."""
    last_vehicle_type = VehicleType.objects.all().order_by('id').last();
    if last_vehicle_type:
        return last_vehicle_type.id + 1
    return 1


class VehicleType(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_vehicle_types'
        verbose_name = _('VehicleType')
        verbose_name_plural = _('VehicleTypes')
        default_permissions = ()
        permissions = (
            ("can_get_vehicle_types", "Can get vehicle_types"),
            ("can_get_vehicle_type", "Can get vehicle_type"),
            ("can_post_vehicle_type", "Can create vehicle_type"),
            ("can_put_vehicle_type", "Can update vehicle_type"),
            ("can_delete_vehicle_type", "Can delete vehicle_type"),
        )

    objects = VehicleTypeManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_vehicle_type_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    text = models.CharField(
        _("Text"),
        max_length=31,
        help_text=_('The text content of this vehicle_type.'),
        db_index=True,
        unique=True
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this vehicle_type.'),
        blank=True,
        null=True,
        default='',
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether vehicle type was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.text)
