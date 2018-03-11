# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
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
from shared_foundation.models.o55_user import O55User
from tenant_foundation.models import (
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

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Customer.objects.filter(
            Q(
                Q(given_name__icontains=keyword) |
                Q(given_name__istartswith=keyword) |
                Q(given_name__iendswith=keyword) |
                Q(given_name__exact=keyword) |
                Q(given_name__icontains=keyword)
            ) | Q(
                Q(middle_name__icontains=keyword) |
                Q(middle_name__istartswith=keyword) |
                Q(middle_name__iendswith=keyword) |
                Q(middle_name__exact=keyword) |
                Q(middle_name__icontains=keyword)
            ) | Q(
                Q(last_name__icontains=keyword) |
                Q(last_name__istartswith=keyword) |
                Q(last_name__iendswith=keyword) |
                Q(last_name__exact=keyword) |
                Q(last_name__icontains=keyword)
            ) | Q(
                Q(email__icontains=keyword) |
                Q(email__istartswith=keyword) |
                Q(email__iendswith=keyword) |
                Q(email__exact=keyword) |
                Q(email__icontains=keyword)
            ) | Q(
                Q(telephone__icontains=keyword) |
                Q(telephone__istartswith=keyword) |
                Q(telephone__iendswith=keyword) |
                Q(telephone__exact=keyword) |
                Q(telephone__icontains=keyword)
            )
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return Customer.objects.annotate(search=SearchVector(
            'organizations__name',
            'given_name',
            'middle_name',
            'last_name',
            # 'business',
            # 'limit_special',
            # 'drivers_license_class',
            # 'how_hear',
            'owner__email',
            'email',
            'telephone'
        ),).filter(search=keyword)


class Customer(AbstractThing, AbstractContactPoint, AbstractPostalAddress, AbstractGeoCoordinate):
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
    #  PERSON FIELDS - http://schema.org/Person
    #

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
    birthdate = models.DateTimeField(
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
        max_length=63,
        help_text=_('Gender of the person. While Male and Female may be used, text strings are also acceptable for people who do not identify as a binary gender.'),
        blank=True,
        null=True,
    )

    #
    #  CUSTOM FIELDS
    #

    is_ok_to_email = models.BooleanField(
        _("Is OK to email"),
        help_text=_('Indicates whether customer allows being reached by email'),
        default=True,
        blank=True
    )
    is_ok_to_text = models.BooleanField(
        _("Is OK to text"),
        help_text=_('Indicates whether customer allows being reached by text.'),
        default=True,
        blank=True
    )
    is_business = models.BooleanField(
        _("Is Business"),
        help_text=_('Indicates whether customer is considered a business representive or not.'),
        default=False,
        blank=True
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
        _("Job information received by"),
        max_length=255,
        help_text=_('The volunteer\'s name whom received this customer.'),
        blank=True,
        null=True,
    )
    how_hear = models.CharField(
        _("Learned about Over 55"),
        max_length=2055,
        help_text=_('How customer heared/learned about this Over 55 Inc.'),
        blank=True,
        null=True,
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments of this customer sorted by latest creation date..'),
        blank=True,
        related_name="%(app_label)s_%(class)s_comments_related",
        through="CustomerComment",
    )
    created_by = models.ForeignKey(
        O55User,
        help_text=_('The user whom created this object.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    last_modified_by = models.ForeignKey(
        O55User,
        help_text=_('The user whom modified this object last.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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

# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='o55_customers.validate_models')
