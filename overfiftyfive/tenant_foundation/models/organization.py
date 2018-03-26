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
from tenant_foundation.models import (
    AbstractContactPoint,
    AbstractGeoCoordinate,
    AbstractPostalAddress,
    AbstractThing
)
from tenant_foundation.utils import *


class OrganizationManager(models.Manager):
    def delete_all(self):
        items = Organization.objects.all()
        for item in items.all():
            item.delete()

class Organization(AbstractThing, AbstractContactPoint, AbstractPostalAddress, AbstractGeoCoordinate):
    """
    An organization such as a library, NGO, corporation, club, etc.

    Source: http://schema.org/Organization
    """
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_organizations'
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        default_permissions = ()
        permissions = (
            ("can_get_organizations", "Can get organizations"),
            ("can_get_organization", "Can get organization"),
            ("can_post_organization", "Can create organization"),
            ("can_put_organization", "Can update organization"),
            ("can_delete_organization", "Can delete organization"),
        )

    objects = OrganizationManager()

    #
    #  SCHEMA FIELDS (see: Source: http://schema.org/Organization)
    #

    naics = models.CharField(
        _("NAICS"),
        max_length=15,
        help_text=_('The North American Industry Classification System (NAICS) code for a particular organization or business person.'),
        blank=True,
        null=True,
    )
    # parent_organization = models.ForeignKey(
    #     "Organization",
    #     help_text=_('The larger organization that this organization is a sub-organization of'),
    #     blank=True,
    #     null=True,
    #     on_delete=models.CASCADE,
    #     related_name="%(app_label)s_%(class)s_parent_organization_related"
    # )

    #
    #  CUSTOM FIELDS
    #
    # (Nothing...)

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.name)
