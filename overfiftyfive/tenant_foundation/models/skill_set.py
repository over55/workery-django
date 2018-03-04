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
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class SkillSetManager(models.Manager):
    def delete_all(self):
        items = SkillSet.objects.all()
        for item in items.all():
            item.delete()


class SkillSet(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_skill_sets'
        verbose_name = _('Skill Set')
        verbose_name_plural = _('Skill Sets')
        default_permissions = ()
        permissions = (
            ("can_get_skill_sets", "Can get skill sets"),
            ("can_get_skill_set", "Can get skill set"),
            ("can_post_skill_set", "Can create skill set"),
            ("can_put_skill_set", "Can update skill set"),
            ("can_delete_skill_set", "Can delete skill set"),
        )

    objects = SkillSetManager()

    #
    #  FIELDS
    #

    category = models.CharField(
        _("Category"),
        max_length=31,
        help_text=_('The category text of this skill set.'),
        db_index=True,
    )
    sub_category = models.CharField(
        _("Sub-Category"),
        max_length=31,
        help_text=_('The sub-category text of this skill set.'),
        db_index=True,
    )
    insurance_requirement = models.CharField(
        _("Insurance Requirement"),
        max_length=63,
        help_text=_('The insurance requirement of this skill set.'),
        db_index=True,
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.category)+" "+str(self.sub_category)
