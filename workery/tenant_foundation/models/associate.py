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
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from starterkit.utils import (
    get_random_string,
    get_unique_username_from_email,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.models import AbstractPerson
from tenant_foundation.utils import *


class AssociateManager(models.Manager):
    def delete_all(self):
        items = Associate.objects.all()
        for item in items.all():
            item.delete()

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return Associate.objects.filter(
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
        return Associate.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)


@transaction.atomic
def increment_associate_id_number():
    """Function will generate a unique big-int."""
    last_associate = Associate.objects.all().order_by('id').last();
    if last_associate:
        return last_associate.id + 1
    return 1


class Associate(AbstractPerson):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_associates'
        verbose_name = _('Associate')
        verbose_name_plural = _('Associates')
        default_permissions = ()
        permissions = (
            ("can_get_associates", "Can get associates"),
            ("can_get_associate", "Can get associate"),
            ("can_post_associate", "Can create associate"),
            ("can_put_associate", "Can update associate"),
            ("can_delete_associate", "Can delete associate"),
        )

    objects = AssociateManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_associate_id_number,
       editable=False,
       db_index=True
    )

    #
    #  PERSON FIELDS (EXTRA) - http://schema.org/Person
    #

    organizations = models.ManyToManyField(
        "Organization",
        help_text=_('The organizations that this associate is affiliated with.'),
        blank=True,
        through='OrganizationAssociateAffiliation'
    )

    #
    #  CUSTOM FIELDS
    #

    business = models.CharField(
        _("Business"),
        max_length=63,
        help_text=_('The associates business status.'),
        blank=True,
        null=True,
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
    is_ok_to_email = models.BooleanField(
        _("Is OK to email"),
        help_text=_('Indicates whether associate allows being reached by email'),
        default=True,
        blank=True
    )
    is_ok_to_text = models.BooleanField(
        _("Is OK to text"),
        help_text=_('Indicates whether associate allows being reached by text.'),
        default=True,
        blank=True
    )
    hourly_salary_desired = models.PositiveSmallIntegerField(
        _("Hourly Salary Desired"),
        help_text=_('The hourly salary rate the associate'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    limit_special = models.CharField(
        _("Limit Special"),
        max_length=255,
        help_text=_('Any special limitations / handicaps this associate has.'),
        blank=True,
        null=True,
    )
    dues_date = models.DateField(
        _("Membership Dues Date"),
        help_text=_('-'),
        null=True,
        blank=True,
    )
    commercial_insurance_expiry_date = models.DateField(
        _("Commercial Insurance Expiry Date"),
        help_text=_('-'),
        null=True,
        blank=True,
    )
    auto_insurance_expiry_date = models.DateField(
        _("Auto Insurance Expiry Date"),
        help_text=_('-'),
        null=True,
        blank=True,
    )
    wsib_insurance_date = models.DateField(
        _("WSIB Insurance Date"),
        help_text=_('-'),
        null=True,
        blank=True,
    )
    police_check = models.DateField(
        _("Police Check"),
        help_text=_('The date the associate took a police check.'),
        null=True,
        blank=True,
    )
    drivers_license_class = models.CharField(
        _("Divers License Class"),
        max_length=31,
        help_text=_('The associates license class for driving.'),
        blank=True,
        null=True,
    )
    how_hear = models.PositiveSmallIntegerField(
        _("How hear"),
        help_text=_('How associate heared about this us from a select range of choices.'),
        blank=True,
        default=8 # Prefer not to say.
    )
    how_hear_other = models.CharField(
        _("How hear (other)"),
        max_length=2055,
        help_text=_('How associate heared about this us in detail.'),
        blank=True,
        null=True,
    )
    vehicle_types = models.ManyToManyField(
        "VehicleType",
        help_text=_('The type of vehicles this associate has for servicing customers.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_vehicle_types_related"
    )
    skill_sets = models.ManyToManyField(
        "SkillSet",
        help_text=_('The skill sets this associate has.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_skill_sets_related"
    )
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
        help_text=_('The tags associated with this associate.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related"
    )
    comments = models.ManyToManyField(
        "Comment",
        help_text=_('The comments belonging to this associate made by other people.'),
        blank=True,
        through='AssociateComment',
        related_name="%(app_label)s_%(class)s_associate_comments_related"
    )
    activity_sheet = models.ManyToManyField(
        "WorkOrder",
        help_text=_('The activity sheet items of the orders the associate accepted or rejected.'),
        blank=True,
        through='ActivitySheetItem',
        related_name="%(app_label)s_%(class)s_activity_sheet_items_related"
    )
    score = models.FloatField(
        _("Score"),
        help_text=_('The score with this associated.'),
        blank=True,
        default=0
    )
    away_log = models.ForeignKey(
        "AwayLog",
        help_text=_('The object referencing our Assocaites away log (if they have one).'),
        related_name="%(app_label)s_%(class)s_away_info_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    insurance_requirements = models.ManyToManyField(
        "InsuranceRequirement",
        help_text=_('The insurance requirements this associate meets.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_insurance_requirements_related"
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether associate was archived.'),
        default=False,
        blank=True,
        db_index=True
    )
    avatar_image = models.ForeignKey(
        "PublicImageUpload",
        help_text=_('The avatar image of this associate.'),
        related_name="%(app_label)s_%(class)s_avatar_image_related",
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
        super(Associate, self).save(*args, **kwargs)

    def past_30_days_activity_sheet_count(self):
        # Get 30 days from right now...
        today = timezone.now()
        today_minus_30_days = today - timedelta(days=30)

        # Count only items within the past 30 days.
        return self.activity_sheet.filter(created__gte=today_minus_30_days).count()


# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='workery_associates.validate_models')
