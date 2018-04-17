# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
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
            Q(indexed_text__icontains=keyword) |
            Q(indexed_text__istartswith=keyword) |
            Q(indexed_text__iendswith=keyword) |
            Q(indexed_text__exact=keyword) |
            Q(indexed_text__icontains=keyword)
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return Staff.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)


@transaction.atomic
def increment_staff_id_number():
    """Function will generate a unique big-int."""
    last_staff = Staff.objects.all().order_by('id').last();
    if last_staff:
        return last_staff.id + 1
    return 1


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
    id = models.BigAutoField(
       primary_key=True,
       default = increment_staff_id_number,
       editable=False,
       db_index=True
    )

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
    birthdate = models.DateField(
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
    join_date = models.DateField(
        _("Join Date"),
        help_text=_('The date the staff member joined this organization.'),
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

    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this staff member.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related"
    )
    skill_sets = models.ManyToManyField(
        "SkillSet",
        help_text=_('The skill sets this staff has.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_skill_sets_related"
    )
    indexed_text = models.CharField(
        _("Indexed Text"),
        max_length=511,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)

    """
    Override the `save` function to support save cached searchable terms.
    """
    def save(self, *args, **kwargs):
        '''
        The following code will populate our indexed_custom search text with
        the latest model data before we save.
        '''
        search_text = str(self.id)
        if self.given_name:
            search_text += " " + self.given_name
        if self.middle_name:
            search_text += " " + self.middle_name
        if self.last_name:
            search_text += " " + self.last_name
        if self.email:
            search_text += " " + self.email
        if self.telephone:
            search_text += " " + phonenumbers.format_number(self.telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
            search_text += " " + phonenumbers.format_number(self.telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            search_text += " " + phonenumbers.format_number(self.telephone, phonenumbers.PhoneNumberFormat.E164)
        if self.other_telephone:
            search_text += " " + phonenumbers.format_number(self.other_telephone, phonenumbers.PhoneNumberFormat.NATIONAL)
            search_text += " " + phonenumbers.format_number(self.other_telephone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            search_text += " " + phonenumbers.format_number(self.other_telephone, phonenumbers.PhoneNumberFormat.E164)
        if self.description:
            search_text += " " + self.description
        self.indexed_text = Truncator(search_text).chars(511)

        '''
        Run our `save` function.
        '''
        super(Staff, self).save(*args, **kwargs)
