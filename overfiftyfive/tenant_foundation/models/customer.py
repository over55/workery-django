# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from tenant_foundation.models import (
    AbstractBigPk,
    AbstractContactPoint,
    AbstractGeoCoordinate,
    AbstractPostalAddress,
    AbstractThing
)
from tenant_foundation.utils import *


class CustomerManager(models.Manager):
    def delete_all(self):
        items = Customer.objects.all()
        for item in items.all():
            item.delete()

    def update_or_create(self, defaults=None, **kwargs):
        """
        Override the `update_or_create` function to work according to our
        specification...

        The 'update_or_create' method tries to fetch an object from database
        based on the given 'kwargs'. If a match is found, it updates the fields
        passed in the 'defaults' dictionary.

        https://docs.djangoproject.com/en/2.0/ref/models/querysets/#django.db.models.query.QuerySet.update_or_create
        """
        try:
            obj = Customer.objects.get(id=kwargs['id'])
            for key, value in defaults.items():
                setattr(obj, key, value)
            obj.save()
            return obj, False
        except Customer.DoesNotExist:
            new_values = defaults
            new_values.update(defaults)
            obj = Customer(**new_values)
            obj.save()
            return obj, True


class Customer(AbstractBigPk, AbstractThing, AbstractContactPoint, AbstractPostalAddress, AbstractGeoCoordinate):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_customers'
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        default_permissions = ()
        permissions = (
            ("can_get_customers", "Can get customers"),
            ("can_get_customer", "Can get customer"),
            ("can_post_customer", "Can create customer"),
            ("can_put_customer", "Can update customer"),
            ("can_delete_customer", "Can delete customer"),
        )

    objects = CustomerManager()

    #
    #  CUSTOM FIELDS
    #

    given_name = models.CharField(
        _("Given Name"),
        max_length=63,
        help_text=_('The customers given name.'),
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The customers last name.'),
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The customers last name.'),
        blank=True,
        null=True,
    )
    birthdate = models.DateTimeField(
        _('Birthdate'),
        help_text=_('The customers birthdate.'),
        blank=True,
        null=True
    )
    is_senior = models.BooleanField(
        _("Is Senior"),
        help_text=_('Indicates whether customer is considered a senior or not.'),
        default=False,
        blank=True
    )
    is_support = models.BooleanField(
        _("Is Support"),
        help_text=_('Indicates whether customer needs support or not.'),
        default=False,
        blank=True
    )
    job_info_read = models.CharField(
        _("Job Info Read"),
        max_length=255,
        help_text=_('-'),
        blank=True,
        null=True,
    )
    how_hear = models.CharField(
        _("How hear"),
        max_length=2055,
        help_text=_('How customer heared about this organization.'),
        blank=True,
        null=True,
    )
    join_date = models.DateTimeField(
        _("Join Date"),
        help_text=_('The date the customer joined this organization.'),
        null=True,
        blank=True,
    )

    #
    #  PERSON FIELDS - http://schema.org/Person
    #

    organizations = models.ManyToManyField(
        "Organization",
        help_text=_('The organizations that this customer is affiliated with.'),
        blank=True,
        through='CustomerAffiliation'
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)

    def save(self, *args, **kwargs):
        """
        Override the "save" function.
        """
        if self.email:
            user = User.objects.filter(email=self.email).first()
            if self.owner:
                if user != self.owner:
                    # print("2 OF 3:")
                    raise ValidationError({
                        'email':'Your email is not unique! Please pick another email.'
                    })
            else:
                email_exists = User.objects.filter(email=self.email).exists()
                if email_exists:
                    # print("1 OF 3:")
                    raise ValidationError({
                        'email':'Your email is not unique! Please pick another email.'
                    })

        # print("3 of 3")
        super(Customer, self).save(*args,**kwargs)


# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='o55_customers.validate_models')
