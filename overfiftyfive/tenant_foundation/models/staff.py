# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
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
from shared_foundation.models.o55_user import O55User
from tenant_foundation.models import (
    AbstractContactPoint,
    AbstractGeoCoordinate,
    AbstractPostalAddress,
    AbstractThing
)
from tenant_foundation.utils import *


# def get_expiry_date(days=2):
#     """Returns the current date plus paramter number of days."""
#     return timezone.now() + timedelta(days=days)


class StaffManager(models.Manager):
    def delete_all(self):
        items = Staff.objects.all()
        for item in items.all():
            item.delete()

    def get_by_email_or_none(self, email):
        try:
            return Staff.objects.get(owner__email=email)
        except Staff.DoesNotExist:
            return None

    def get_by_user_or_none(self, user):
        try:
            return Staff.objects.get(owner=user)
        except Staff.DoesNotExist:
            return None

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Staff.objects.filter(
            Q(
                Q(given_name__icontains=keyword) |
                Q(given_name__istartswith=keyword) |
                Q(given_name__iendswith=keyword) |
                Q(given_name__exact=keyword)
            ) | Q(
                Q(middle_name__icontains=keyword) |
                Q(middle_name__istartswith=keyword) |
                Q(middle_name__iendswith=keyword) |
                Q(middle_name__exact=keyword)
            ) | Q(
                Q(last_name__icontains=keyword) |
                Q(last_name__istartswith=keyword) |
                Q(last_name__iendswith=keyword) |
                Q(last_name__exact=keyword)
            ) | Q(
                Q(email__icontains=keyword) |
                Q(email__istartswith=keyword) |
                Q(email__iendswith=keyword) |
                Q(email__exact=keyword)
            ) | Q(
                Q(telephone__icontains=keyword) |
                Q(telephone__istartswith=keyword) |
                Q(telephone__iendswith=keyword) |
                Q(telephone__exact=keyword)
            )
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return Staff.objects.annotate(search=SearchVector(
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


class Staff(AbstractThing, AbstractContactPoint, AbstractPostalAddress, AbstractGeoCoordinate):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_staff'
        verbose_name = _('Staff')
        verbose_name_plural = _('Staves')
        default_permissions = ()
        permissions = (
            ("can_get_staves", "Can get staves"),
            ("can_get_staff", "Can get staff"),
            ("can_post_staff", "Can create staff"),
            ("can_put_staff", "Can update staff"),
            ("can_delete_staff", "Can delete staff"),
        )

    objects = StaffManager()

    #
    #  PERSON FIELDS - http://schema.org/Person
    #

    given_name = models.CharField(
        _("Given Name"),
        max_length=63,
        help_text=_('The staff members given name.'),
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The staff members last name.'),
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The staff members last name.'),
        blank=True,
        null=True,
    )
    birthdate = models.DateTimeField(
        _('Birthdate'),
        help_text=_('The staff members birthdate.'),
        blank=True,
        null=True
    )
    how_hear = models.CharField(
        _("How hear"),
        max_length=2055,
        help_text=_('How this staff member heared about this organization.'),
        blank=True,
        null=True,
    )
    join_date = models.DateTimeField(
        _("Join Date"),
        help_text=_('The date the staff member joined this organization.'),
        null=True,
        blank=True,
    )

    #
    #  CUSTOM FIELDS
    #

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
    # comments = models.ManyToManyField(
    #     "Comment",
    #     help_text=_('The comments of this associate sorted by latest creation date..'),
    #     blank=True,
    #     related_name="%(app_label)s_%(class)s_associate_related",
    #     through="AssociateComment",
    # )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)
