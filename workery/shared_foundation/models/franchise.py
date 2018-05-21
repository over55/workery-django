# -*- coding: utf-8 -*-
import csv
from datetime import date, datetime, timedelta
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin
from shared_foundation import constants
from shared_foundation.models.abstract_thing import AbstractSharedThing
from shared_foundation.models.abstract_contact_point import AbstractSharedContactPoint
from shared_foundation.models.abstract_postal_address import AbstractSharedPostalAddress
from shared_foundation.models.abstract_geo_coorindate import AbstractSharedGeoCoordinate
from shared_foundation.models.user import SharedUser


class SharedFranchiseManager(models.Manager):
    def delete_all(self):
        items = SharedFranchise.objects.all()
        for item in items.all():
            item.delete()


class SharedFranchise(TenantMixin, AbstractSharedThing, AbstractSharedContactPoint, AbstractSharedPostalAddress, AbstractSharedGeoCoordinate):
    """
    Model is the tenant in our system.
    """

    class Meta:
        app_label = 'shared_foundation'
        db_table = 'workery_franchises'
        verbose_name = _('Franchise')
        verbose_name_plural = _('Franchises')
        default_permissions = ()
        permissions = (
            ("can_get_franchises", "Can get franchises"),
            ("can_get_franchise", "Can get franchise"),
            ("can_post_franchise", "Can post franchise"),
            ("can_put_franchise", "Can put franchise"),
            ("can_delete_franchise", "Can delete franchise"),
        )

    objects = SharedFranchiseManager()
    currency = models.CharField(
        _("Currency"),
        max_length=3,
        help_text=_('The currency used by this franchise formatted in <a href="https://en.wikipedia.org/wiki/ISO_4217">ISO 4217</a> formatting.'),
        default="CAN",
        blank=True,
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether this franchise was archived.'),
        default=False,
        blank=True,
        db_index=True
    )

    #
    #  Custom Fields
    #

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.name)

    def reverse(self, reverse_id, reverse_args=[]):
        return settings.O55_APP_HTTP_PROTOCOL + str(self.schema_name) + "." + settings.O55_APP_HTTP_DOMAIN + reverse(reverse_id, args=reverse_args)

    def is_public(self):
        """
        Function returns boolean value as to whether this franchise is the
        public or a tenant.
        """
        return self.schema_name == "public" or self.schema_name == "test"

class SharedFranchiseDomain(DomainMixin):
    class Meta:
        app_label = 'shared_foundation'
        db_table = 'workery_franchise_domains'
        verbose_name = _('Domain')
        verbose_name_plural = _('Domains')

    pass
