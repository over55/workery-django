# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tenant_foundation.models import (
    AbstractContactPoint,
    AbstractGeoCoordinate,
    AbstractPostalAddress,
    AbstractThing
)
from tenant_foundation.utils import *


class AbstractPerson(AbstractThing, AbstractContactPoint, AbstractPostalAddress, AbstractGeoCoordinate):
    """
    http://schema.org/Person
    """
    class Meta:
        abstract = True

    given_name = models.CharField(
        _("Given Name"),
        max_length=63,
        help_text=_('The customers given name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The customers last name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The customers last name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    birthdate = models.DateField(
        _('Birthdate'),
        help_text=_('The customers birthdate.'),
        blank=True,
        null=True
    )
    join_date = models.DateTimeField(
        _("Join Date"),
        help_text=_('The date the customer joined this organization.'),
        null=True,
        blank=True,
    )
    nationality = models.CharField(
        _("Nationality"),
        max_length=63,
        help_text=_('Nationality of the person.'),
        blank=True,
        null=True,
    )
    gender = models.CharField(
        _("Gender"),
        max_length=31,
        help_text=_('Gender of the person. While Male and Female may be used, text strings are also acceptable for people who do not identify as a binary gender.'),
        blank=True,
        null=True,
    )
    tax_id = models.CharField(
        _("Tax ID"),
        max_length=127,
        help_text=_('The Tax / Fiscal ID of the organization or person, e.g. the TIN in the US or the CIF/NIF in Spain.'),
        blank=True,
        null=True,
    )
