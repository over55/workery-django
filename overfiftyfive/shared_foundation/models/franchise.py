# -*- coding: utf-8 -*-
import csv
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
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
from shared_foundation.models.o55_user import O55User


class SharedFranchiseManager(models.Manager):
    def get_by_email_or_none(self, email):
        try:
            return SharedFranchise.objects.get(
                Q(managers__email=email) |
                Q(frontline_staff__email=email) |
                Q(customers__email=email)
            )
        except SharedFranchise.DoesNotExist:
            return None


class SharedFranchise(TenantMixin, AbstractSharedThing, AbstractSharedContactPoint, AbstractSharedPostalAddress, AbstractSharedGeoCoordinate):
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
    #  Custom Fields
    #

    managers = models.ManyToManyField(
        O55User,
        help_text=_('The managers who belong to this "Franchise" and are administrators or have executive decision making authority.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_managers_related"
    )
    frontline_staff = models.ManyToManyField(
        O55User,
        help_text=_('The office staff and or volunteers who belong to this "Franchise".'),
        blank=True,
        related_name="%(app_label)s_%(class)s_frontline_staff_related"
    )
    customers = models.ManyToManyField(
        O55User,
        help_text=_('The customers who belong to this "Franchise".'),
        blank=True,
        related_name="%(app_label)s_%(class)s_customers_related"
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.name)

    def reverse(self, reverse_id, reverse_args=[]):
        return settings.O55_APP_HTTP_PROTOCOL + str(self.schema_name) + "." + settings.O55_APP_HTTP_DOMAIN + reverse(reverse_id, args=reverse_args)


class SharedFranchiseDomain(DomainMixin):
    class Meta:
        app_label = 'shared_foundation'
        db_table = 'o55_franchise_domains'
        verbose_name = _('Domain')
        verbose_name_plural = _('Domains')

    pass
