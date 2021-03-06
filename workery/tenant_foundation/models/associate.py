# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from phonenumber_field.modelfields import PhoneNumberField
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from djmoney.money import Money
from djmoney.models.fields import MoneyField
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.aggregates import StringAgg
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.db.models import Q
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.constants import *
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

    def get_associate_with_user_id(self, user_id):
        cache_key  = 'associate_id_for_user_id_' + str(user_id)
        associate_id = cache.get(cache_key)
        if associate_id:
            return Associate.objects.filter(id=associate_id).first()

        associate = Associate.objects.filter(owner__id=user_id).first()
        cache.set(cache_key, associate.id, None)
        return associate


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

    organizations = models.ManyToManyField( # DEPRECATED
        "Organization",
        help_text=_('The organizations that this associate is affiliated with.'),
        blank=True,
        through='OrganizationAssociateAffiliation'
    )

    #
    #  ORGANIZATION FIELDS
    #

    organization_name = models.CharField(
        _("Organization Name"),
        max_length=255,
        help_text=_('The name of the organization or business this person represents.'),
        blank=True,
        null=True,
    )
    organization_type_of = models.PositiveSmallIntegerField(
        _("Organization Type of"),
        help_text=_('The type of organization this is based on Over55 internal classification.'),
        default=UNKNOWN_ORGANIZATION_TYPE_OF_ID,
        blank=True,
        choices=ORGANIZATION_TYPE_OF_CHOICES,
    )

    #
    #  CUSTOM FIELDS
    #

    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of customer this is.'),
        default=UNASSIGNED_ASSOCIATE_TYPE_OF_ID,
        blank=True,
        choices=ASSOCIATE_TYPE_OF_CHOICES,
        db_index=True,
    )
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
    wsib_number = models.CharField(
        _("WSIB #"),
        max_length=127,
        help_text=_('Assigned WSIB number to this associate.'),
        blank=True,
        null=True,
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
    how_hear_old = models.PositiveSmallIntegerField(
        _("Learned about us (old)"),
        help_text=_('How associate heared about this us from a select range of choices.'),
        blank=True,
        default=8 # Prefer not to say.
    )
    how_hear = models.ForeignKey(
        "HowHearAboutUsItem",
        help_text=_('How associate heared about this us from a select range of choices.'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="associates"
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
        related_name="created_associates",
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
        related_name="last_modified_associates",
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
        related_name="associates",
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
        "PrivateImageUpload",
        help_text=_('The avatar image of this associate.'),
        related_name="associates",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    balance_owing_amount = MoneyField(
        _("Balance Owing Amount"),
        help_text=_('The amount remaining to be paid by the associate for service fee for this job.'),
        max_digits=10,
        decimal_places=2,
        default_currency=WORKERY_APP_DEFAULT_MONEY_CURRENCY,
        default=Money(0,WORKERY_APP_DEFAULT_MONEY_CURRENCY),
        blank=True,
    )
    emergency_contact_name = models.CharField(
        _("Emergency contact full-name"),
        max_length=127,
        help_text=_('The name of this associate\'s primary contact.'),
        blank=True,
        null=True,
    )
    emergency_contact_relationship = models.CharField(
        _("Emergency contact relationship"),
        max_length=127,
        help_text=_('The relationship of this associate\'s primary contact.'),
        blank=True,
        null=True,
    )
    emergency_contact_telephone = PhoneNumberField(
        _("Emergency contact telephone"),
        help_text=_('The telephone of this associate\'s primary contact.'),
        blank=True,
        null=True,
    )
    emergency_contact_alternative_telephone = PhoneNumberField(
        _("Emergency contact alternative telephone"),
        help_text=_('The alternative telephone of this associate\'s primary contact.'),
        blank=True,
        null=True,
    )
    service_fee = models.ForeignKey(
        "WorkOrderServiceFee",
        help_text=_('The service fee assigned for this associate.'),
        related_name="associates",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)

    def get_pretty_name(self):
        """
        Function will format the name output to add the organization name if
        there is one.
        """
        if self.organization_name:
            return self.organization_name
        else:
            return str(self)

    """
    Override the `save` function to support save cached searchable terms.
    """
    def save(self, *args, **kwargs):
        '''
        The following code will populate our indexed_custom search text with
        the latest model data before we save.
        '''
        search_text = str(self.id)
        search_text += " " + intcomma(self.id)
        if self.last_name:
            search_text += " " + self.last_name
        if self.middle_name:
            search_text += " " + self.middle_name
        if self.given_name:
            search_text += " " + self.given_name
        if self.organization_name:
            search_text += " " + self.organization_name
        search_text += " " + str(self.id)
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
        search_text += " " + self.get_postal_address()
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

    def get_skill_sets_string(self):
        # Attach all the skill sets that are associated with each job.
        skill_set_count = self.skill_sets.count() - 1
        skill_set_string = ""
        for i, skill_set in enumerate(self.skill_sets.all()):

            skill_set_string += skill_set.sub_category

            if i != skill_set_count:
                skill_set_string += "|"
            else:
                pass # Skip last
        return skill_set_string

    def get_insurance_requirements(self):
        # Attach all the skill sets that are associated with each job.
        insurance_requirements_count = self.insurance_requirements.count() - 1
        insurance_requirements_string = ""
        for i, insurance_requirements in enumerate(self.insurance_requirements.all()):
            insurance_requirements_string += insurance_requirements.text

            if i != insurance_requirements_count:
                insurance_requirements_string += "|"
            else:
                pass # Skip last
        return insurance_requirements_string

    def get_current_age(self):
        if self.birthdate:
            now_dt = datetime.now()
            difference_in_years = relativedelta(now_dt, self.birthdate).years
            return difference_in_years
        return None

    @cached_property
    def latest_completed_and_paid_order(self):
        """
        Returns the last work order which the associate paid their membership
        fees completely
        """
        from tenant_foundation.models.work_order import WORK_ORDER_STATE
        return self.work_orders.filter(state=WORK_ORDER_STATE.COMPLETED_AND_PAID).latest('id')

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'latest_completed_and_paid_order':
                del self.latest_completed_and_paid_order
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    def get_organization_type_of_label(self):
        choice = dict(ORGANIZATION_TYPE_OF_CHOICES).get(self.organization_type_of)
        return str(choice)

    def invalidate_all(self):
        self.invalidate("latest_completed_and_paid_order")

# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='workery_associates.validate_models')
