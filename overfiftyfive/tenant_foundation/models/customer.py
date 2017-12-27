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
    AbstractBigPk,
    AbstractGeoCoordinate,
    AbstractPostalAddress
)
from tenant_foundation.utils import *


class CustomerManager(models.Manager):
    def delete_all(self):
        items = Customer.objects.all()
        for item in items.all():
            item.delete()


class Customer(AbstractBigPk, AbstractPostalAddress, AbstractGeoCoordinate):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_customers'
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    objects = CustomerManager()

    #
    #  CUSTOM FIELDS
    #

    given_name = models.CharField(
        _("Given Name"),
        max_length=63,
        help_text=_('The employees given name.'),
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The employees last name.'),
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The employees last name.'),
        blank=True,
        null=True,
    )

    #
    #  SYSTEM FIELDS
    #

    user = models.OneToOneField(
        User,
        help_text=_('The user whom owns this customer.'),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_index=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    last_modified = models.DateTimeField(auto_now=True, db_index=True,)

    #
    #  FUNCTIONS
    #

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)
