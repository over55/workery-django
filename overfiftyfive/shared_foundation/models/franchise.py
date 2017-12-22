# -*- coding: utf-8 -*-
import csv
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin
from shared_foundation import constants


class SharedFranchiseManager(models.Manager):
    def delete_all(self):
        items = SharedFranchise.objects.all()
        for item in items.all():
            item.delete()


class SharedFranchise(TenantMixin):
    """
    Model is the tenant in our system.
    """

    class Meta:
        app_label = 'shared_foundation'
        db_table = 'o55_franchises'
        verbose_name = _('Franchise')
        verbose_name_plural = _('Franchises')

    objects = SharedFranchiseManager()

    #
    #  FIELDS
    #

    name = models.CharField(
        _("Name"),
        max_length=127,
        help_text=_('The official name of this Franchise.'),
    )
    alternate_name = models.CharField(
        _("Alternate Name"),
        max_length=127,
        help_text=_('An alias for this Franchise.'),
        blank=True,
        null=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('The detailed description about this Franchise.'),
        blank=True
    )

    #
    #  SYSTEM FIELDS
    #
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    last_modified = models.DateTimeField(auto_now=True, db_index=True,)

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.description)




class SharedFranchiseDomain(DomainMixin):
    class Meta:
        app_label = 'shared_foundation'
        db_table = 'o55_franchise_domains'
        verbose_name = _('Domain')
        verbose_name_plural = _('Domains')

    pass
