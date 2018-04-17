# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db import transaction
from django.db.models import Q
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
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
        return Customer.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)


@transaction.atomic
def increment_customer_id_number():
    """Function will generate a unique big-int."""
    last_customer = Customer.objects.all().order_by('id').last();
    if last_customer:
        return last_customer.id + 1
    return 1


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
    id = models.BigAutoField(
       primary_key=True,
       default = increment_customer_id_number,
       editable=False,
       db_index=True
    )

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
        max_length=63,
        help_text=_('Gender of the person. While Male and Female may be used, text strings are also acceptable for people who do not identify as a binary gender.'),
        blank=True,
        null=True,
    )

    #
    #  CUSTOM FIELDS
    #

    indexed_text = models.CharField(
        _("Indexed Text"),
        max_length=511,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of customer this is.'),
        default=UNASSIGNED_CUSTOMER_TYPE_OF_ID,
        blank=True,
        choices=CUSTOMER_TYPE_OF_CHOICES,
        db_index=True,
    )
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
        help_text=_('The tags associated with this customer.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related"
    )
    skill_sets = models.ManyToManyField(
        "SkillSet",
        help_text=_('The skill sets this customer has.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_skill_sets_related"
    )

    #
    #  PERSON FIELDS - http://schema.org/Person
    #

    organization = models.ForeignKey(
        "Organization",
        help_text=_('The organization that this customer is affiliated with.'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
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
        super(Customer, self).save(*args, **kwargs)

# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='o55_customers.validate_models')
