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


class AssociateManager(models.Manager):
    def delete_all(self):
        items = Associate.objects.all()
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
            obj = Associate.objects.get(id=kwargs['id'])
            for key, value in defaults.items():
                setattr(obj, key, value)
            obj.save()
            return obj, False
        except Associate.DoesNotExist:
            new_values = defaults
            new_values.update(defaults)
            obj = Associate(**new_values)
            obj.save()
            return obj, True


class Associate(AbstractBigPk, AbstractThing, AbstractContactPoint, AbstractPostalAddress, AbstractGeoCoordinate):
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

    #
    #  CUSTOM FIELDS
    #

    given_name = models.CharField(
        _("Given Name"),
        max_length=63,
        help_text=_('The employees given name.'),
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The employees last name.'),
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The employees last name.'),
        blank=True,
        null=True,
    )
    business = models.CharField(
        _("Business"),
        max_length=63,
        help_text=_('The employees business status.'),
        blank=True,
        null=True,
    )
    birthdate = models.DateTimeField(
        _('Birthdate'),
        help_text=_('The employees birthdate.'),
        blank=True,
        null=True
    )
    join_date = models.DateTimeField(
        _("Join Date"),
        help_text=_('The date the employee joined.'),
        null=True,
        blank=True,
    )
    hourly_salary_desired = models.PositiveSmallIntegerField(
        _("Hourly Salary Desired"),
        help_text=_('The hourly salary rate the employee'),
        null=True,
        blank=True,
    )
    limit_special = models.CharField(
        _("Limit Special"),
        max_length=255,
        help_text=_('Any special limitations / handicaps this employee has.'),
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
        help_text=_('The date the employee took a police check.'),
        null=True,
        blank=True,
    )
    comments = models.CharField(
        _("Comments"),
        max_length=1027,
        help_text=_('The comments associated with this employee.'),
        blank=True,
        null=True,
    )
    drivers_license_class = models.CharField(
        _("Divers License Class"),
        max_length=7,
        help_text=_('The employees license class for driving.'),
        blank=True,
        null=True,
    )
    has_car = models.BooleanField(
        _("Has Car"),
        help_text=_('Indicates whether employee has a car or not.'),
        default=False,
        blank=True
    )
    has_van = models.BooleanField(
        _("Has Van"),
        help_text=_('Indicates whether employee has a van or not.'),
        default=False,
        blank=True
    )
    has_truck = models.BooleanField(
        _("Has Truck"),
        help_text=_('Indicates whether employee has a truck or not.'),
        default=False,
        blank=True
    )
    is_full_time = models.BooleanField(
        _("Is Full Time"),
        help_text=_('Indicates whether employee is full time or not.'),
        default=False,
        blank=True
    )
    is_part_time = models.BooleanField(
        _("Is Part Time"),
        help_text=_('Indicates whether employee is part time or not.'),
        default=False,
        blank=True
    )
    is_contract_time = models.BooleanField(
        _("Is Contract Time"),
        help_text=_('Indicates whether employee is contracted or not.'),
        default=False,
        blank=True
    )
    is_small_job = models.BooleanField(
        _("Is Small Job"),
        help_text=_('Indicates whether employee is employed for small jobs or not.'),
        default=False,
        blank=True
    )
    how_hear = models.CharField(
        _("How hear"),
        max_length=2055,
        help_text=_('How employee heared about this business.'),
        blank=True,
        null=True,
    )

    #
    #  PERSON FIELDS - http://schema.org/Person
    #

    organizations = models.ManyToManyField(
        "Organization",
        help_text=_('The organizations that this associate is affiliated with.'),
        blank=True,
        through='AssociateAffiliation'
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
        super(Associate, self).save(*args,**kwargs)


# def validate_model(sender, **kwargs):
#     if 'raw' in kwargs and not kwargs['raw']:
#         kwargs['instance'].full_clean()
#
# pre_save.connect(validate_model, dispatch_uid='o55_associates.validate_models')
