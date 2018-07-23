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
from tenant_foundation.models import AbstractPerson
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


class Customer(AbstractPerson):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_customers'
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
    # how_hear = models.PositiveSmallIntegerField(
    #     _("Learned about us"),
    #     help_text=_('How customer heared/learned about this Over 55 Inc.'),
    #     blank=True,
    #     null=True,
    # )
    how_hear_other = models.CharField(
        _("Learned about us (other)"),
        max_length=2055,
        help_text=_('How customer heared/learned about this Over 55 Inc.'),
        blank=True,
        null=True,
    )
    """
    how_hear = models.PositiveSmallIntegerField(
        _("Learned about us"),
        help_text=_('How customer heared/learned about this Over 55 Inc.'),
        blank=True,
        default=1 # 1 = Other
    )
    how_hear_other = models.CharField(
        _("Learned about us (other)"),
        max_length=2055,
        help_text=_('How customer heared/learned about this Over 55 Inc.'),
        blank=True,
        default="Did not answer"
    )
    """
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this customer.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related"
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments belonging to this customer made by other people.'),
        blank=True,
        through='CustomerComment',
        related_name="%(app_label)s_%(class)s_customer_comments_related"
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether customer was archived.'),
        default=True,
        blank=True,
        db_index=True
    )
    avatar_image = models.ForeignKey(
        "PublicImageUpload",
        help_text=_('The avatar image of this customer.'),
        related_name="%(app_label)s_%(class)s_avatar_image_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    #
    #  PERSON FIELDS (EXTRA) - http://schema.org/Person
    #

    organization = models.ForeignKey(
        "Organization",
        help_text=_('The organization that this customer is affiliated with.'),
        blank=False,
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

    def get_pretty_how_hear(self):
        """
        Return a user-friendly `how_hear` pretty formatted output.
        """
        if self.how_hear == 2:
            return _('A friend or family member')
        elif self.how_hear == 3:
            return _('Google')
        elif self.how_hear == 5:
            return _('An Over 55 Associate')
        elif self.how_hear == 6:
            return _('Facebook')
        elif self.how_hear == 7:
            return _('Twitter')
        elif self.how_hear == 8:
            return _('Instagram')
        elif self.how_hear == 9:
            return _('Magazine Ad')
        elif self.how_hear == 10:
            return _('Event')
        else:
            return self.how_hear_other

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
# pre_save.connect(validate_model, dispatch_uid='workery_customers.validate_models')
