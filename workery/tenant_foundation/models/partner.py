# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.aggregates import StringAgg
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.models import AbstractPerson
from tenant_foundation.utils import *


class PartnerManager(models.Manager):
    def delete_all(self):
        items = Partner.objects.all()
        for item in items.all():
            item.delete()

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Partner.objects.filter(
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
        return Partner.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)


@transaction.atomic
def increment_partner_id_number():
    """Function will generate a unique big-int."""
    last_partner = Partner.objects.all().order_by('id').last();
    if last_partner:
        return last_partner.id + 1
    return 1


class Partner(AbstractPerson):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_partners'
        verbose_name = _('Partner')
        verbose_name_plural = _('Partners')
        default_permissions = ()
        permissions = (
            ("can_get_partners", "Can get partners"),
            ("can_get_partner", "Can get partner"),
            ("can_post_partner", "Can create partner"),
            ("can_put_partner", "Can update partner"),
            ("can_delete_partner", "Can delete partner"),
        )

    objects = PartnerManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_partner_id_number,
       editable=False,
       db_index=True
    )

    #
    #  PERSON FIELDS (EXTRA) - http://schema.org/Person
    #

    organization = models.ForeignKey(
        "Organization",
        help_text=_('The organization that this partner that is affiliated with.'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="partners",
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
    is_ok_to_email = models.BooleanField(
        _("Is OK to email"),
        help_text=_('Indicates whether partner allows being reached by email'),
        default=True,
        blank=True
    )
    is_ok_to_text = models.BooleanField(
        _("Is OK to text"),
        help_text=_('Indicates whether partner allows being reached by text.'),
        default=True,
        blank=True
    )
    how_hear = models.CharField(
        _("How hear"),
        max_length=2055,
        help_text=_('How partner heared about this business.'),
        blank=True,
        null=True,
    )
    how_hear_about_us = models.ForeignKey(
        "HowHearAboutUsItem",
        help_text=_('How partner heared about this business.'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="partners"
    )
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_partners",
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
        related_name="last_modified_partners",
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
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments belonging to this partner made by other people.'),
        blank=True,
        through='PartnerComment',
        related_name="%(app_label)s_%(class)s_partner_comments_related"
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether partner was archived.'),
        default=False,
        blank=True,
        db_index=True
    )
    avatar_image = models.ForeignKey(
        "PublicImageUpload",
        help_text=_('The avatar image of this partner.'),
        related_name="partners",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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
        super(Partner, self).save(*args, **kwargs)


# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='workery_partners.validate_models')
