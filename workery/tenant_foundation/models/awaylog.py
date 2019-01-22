# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from django.conf import settings
from django.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from shared_foundation.models import SharedUser
from tenant_foundation.utils import *


class AwayLogManager(models.Manager):
    def delete_all(self):
        items = AwayLog.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_away_log_id_number():
    """Function will generate a unique big-int."""
    away_log = AwayLog.objects.all().order_by('id').last();
    if away_log:
        return away_log.id + 1
    return 1


class AwayLog(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_away_logs'
        verbose_name = _('AwayLog')
        verbose_name_plural = _('AwayLogs')
        default_permissions = ()
        permissions = (
            ("can_get_away_logs", "Can get away logs"),
            ("can_get_away_log", "Can get away log"),
            ("can_post_away_log", "Can create away log"),
            ("can_put_away_log", "Can update away log"),
            ("can_delete_away_log", "Can delete away log"),
        )

    objects = AwayLogManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_away_log_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our away log.'),
        related_name="away_logs",
        on_delete=models.CASCADE,
    )
    reason = models.PositiveSmallIntegerField(
        _("Reason"),
        help_text=_('The reason the user is away.'),
        blank=True,
        null=True,
        default=0,
    )
    reason_other = models.CharField(
        _("Reason other"),
        help_text=_('A specific reason the user is away.'),
        max_length=511,
        blank=True,
        null=True,
        default='',
    )
    until_further_notice = models.BooleanField(
        _("Away until further notice"),
        help_text=_('Track whether .'),
        default=False,
        blank=True
    )
    until_date = models.DateField(
        _('Away until date'),
        help_text=_('The date that this user will return on.'),
        blank=True,
        null=True
    )
    start_date = models.DateField(
        _('Away start date'),
        help_text=_('The date that this user will start their absence on.'),
        blank=True,
        null=True
    )
    was_deleted = models.BooleanField(
        _("Was deleted"),
        help_text=_('Track whether this away log was deleted or not.'),
        default=False,
        blank=True,
        db_index=True
    )

    #
    #  SYSTEM
    #
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this away log.'),
        related_name="created_away_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this away log.'),
        related_name="last_modified_away_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.pk)
