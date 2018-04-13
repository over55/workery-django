# -*- coding: utf-8 -*-
import csv
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
from tenant_foundation.models import (
    AbstractContactPoint,
    AbstractGeoCoordinate,
    AbstractPostalAddress,
    AbstractThing
)
from tenant_foundation.utils import *


class AssociateManager(models.Manager):
    def delete_all(self):
        items = Associate.objects.all()
        for item in items.all():
            item.delete()

    def partial_text_search(self, keyword):
        """Function performs parital text search of various textfields."""
        return Associate.objects.filter(
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
        return Associate.objects.annotate(search=SearchVector(
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


@transaction.atomic
def increment_associate_id_number():
    """Function will generate a unique big-int."""
    last_associate = Associate.objects.all().order_by('id').last();
    if last_associate:
        return last_associate.id + 1
    return 1


class Associate(AbstractThing, AbstractContactPoint, AbstractPostalAddress, AbstractGeoCoordinate):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_associates'
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
    #  PERSON FIELDS - http://schema.org/Person
    #

    organizations = models.ManyToManyField(
        "Organization",
        help_text=_('The organizations that this associate is affiliated with.'),
        blank=True,
        through='OrganizationAssociateAffiliation'
    )

    given_name = models.CharField(
        _("Given Name"),
        max_length=63,
        help_text=_('The associates given name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The associates last name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The associates last name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    business = models.CharField(
        _("Business"),
        max_length=63,
        help_text=_('The associates business status.'),
        blank=True,
        null=True,
    )
    birthdate = models.DateField(
        _('Birthdate'),
        help_text=_('The associates birthdate.'),
        blank=True,
        null=True
    )
    join_date = models.DateTimeField(
        _("Join Date"),
        help_text=_('The date the associate joined.'),
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
    )
    limit_special = models.CharField(
        _("Limit Special"),
        max_length=255,
        help_text=_('Any special limitations / handicaps this associate has.'),
        blank=True,
        null=True,
    )
    dues_pd = models.DateTimeField(
        _("Deus PD"),
        help_text=_('-'),
        null=True,
        blank=True,
    )
    ins_due = models.DateTimeField(
        _("Ins Due"),
        help_text=_('-'),
        null=True,
        blank=True,
    )
    police_check = models.DateTimeField(
        _("Police Check"),
        help_text=_('The date the associate took a police check.'),
        null=True,
        blank=True,
    )
    drivers_license_class = models.CharField(
        _("Divers License Class"),
        max_length=7,
        help_text=_('The associates license class for driving.'),
        blank=True,
        null=True,
    )
    has_car = models.BooleanField(
        _("Has Car"),
        help_text=_('Indicates whether associate has a car or not.'),
        default=False,
        blank=True
    )
    has_van = models.BooleanField(
        _("Has Van"),
        help_text=_('Indicates whether associate has a van or not.'),
        default=False,
        blank=True
    )
    has_truck = models.BooleanField(
        _("Has Truck"),
        help_text=_('Indicates whether associate has a truck or not.'),
        default=False,
        blank=True
    )
    is_full_time = models.BooleanField(
        _("Is Full Time"),
        help_text=_('Indicates whether associate is full time or not.'),
        default=False,
        blank=True
    )
    is_part_time = models.BooleanField(
        _("Is Part Time"),
        help_text=_('Indicates whether associate is part time or not.'),
        default=False,
        blank=True
    )
    is_contract_time = models.BooleanField(
        _("Is Contract Time"),
        help_text=_('Indicates whether associate is contracted or not.'),
        default=False,
        blank=True
    )
    is_small_job = models.BooleanField(
        _("Is Small Job"),
        help_text=_('Indicates whether associate is employed for small jobs or not.'),
        default=False,
        blank=True
    )
    how_hear = models.CharField(
        _("How hear"),
        max_length=2055,
        help_text=_('How associate heared about this business.'),
        blank=True,
        null=True,
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
        help_text=_('The tags associated with this associate.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_tags_related"
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)

    # def save(self, *args, **kwargs):
    #     """
    #     Override the "save" function.
    #     """
    #     if self.email:
    #         user = SharedUser.objects.filter(email=self.email).first()
    #         if self.owner:
    #             if user != self.owner:
    #                 # print("2 OF 3:")
    #                 raise ValidationError({
    #                     'email':'Your email is not unique! Please pick another email.'
    #                 })
    #         else:
    #             email_exists = SharedUser.objects.filter(email=self.email).exists()
    #             if email_exists:
    #                 # print("1 OF 3:")
    #                 raise ValidationError({
    #                     'email':'Your email is not unique! Please pick another email.'
    #                 })
    #
    #     # print("3 of 3")
    #     super(Associate, self).save(*args,**kwargs)


# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='o55_associates.validate_models')
