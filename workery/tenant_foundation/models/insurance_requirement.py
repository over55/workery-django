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


class InsuranceRequirementManager(models.Manager):
    def delete_all(self):
        items = InsuranceRequirement.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_insurance_requirement_id_number():
    """Function will generate a unique big-int."""
    last_insurance_requirement = InsuranceRequirement.objects.all().order_by('id').last();
    if last_insurance_requirement:
        return last_insurance_requirement.id + 1
    return 1


class InsuranceRequirement(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_insurance_requirements'
        verbose_name = _('Insurance Requirement')
        verbose_name_plural = _('Insurance Requirements')
        default_permissions = ()
        permissions = (
            ("can_get_insurance_requirements", "Can get insurance_requirements"),
            ("can_get_insurance_requirement", "Can get insurance_requirement"),
            ("can_post_insurance_requirement", "Can create insurance_requirement"),
            ("can_put_insurance_requirement", "Can update insurance_requirement"),
            ("can_delete_insurance_requirement", "Can delete insurance_requirement"),
        )

    objects = InsuranceRequirementManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_insurance_requirement_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    text = models.CharField(
        _("Text"),
        max_length=31,
        help_text=_('The text content of this insurance requirement.'),
        db_index=True,
        unique=True
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this insurance requirement.'),
        blank=True,
        null=True,
        default='',
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
