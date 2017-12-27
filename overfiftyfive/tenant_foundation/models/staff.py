# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
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
from tenant_foundation.models import AbstractBigPk
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
            return Staff.objects.get(user__email=email)
        except Staff.DoesNotExist:
            return None

    def get_by_user_or_none(self, user):
        try:
            return Staff.objects.get(user=user)
        except Staff.DoesNotExist:
            return None


class Staff(AbstractBigPk):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_staff'
        verbose_name = _('Staff')
        verbose_name_plural = _('Staves')

    objects = StaffManager()

    #
    #  FIELDS
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
    is_active = models.BooleanField(
        _("Is Active"),
        help_text=_('Track whether this employee is active.'),
        default=False,
        blank=True
    )
    birthdate = models.DateTimeField(
        _('Birthdate'),
        help_text=_('The employees birthdate.'),
        blank=True,
        null=True
    )
    address = models.CharField(
        _("Address"),
        max_length=127,
        help_text=_('The employees address.'),
        blank=True,
        null=True,
    )
    join_date = models.DateTimeField(
        _("Join Date"),
        help_text=_('The date the employee joined.'),
        null=True,
        blank=True,
    )
    phone = models.CharField(
        _("Phone Number"),
        max_length=16,
        help_text=_('The phone number of the employee.'),
        db_index=True,
        validators=[],
        blank=True,
        null=True,
    )
    fax = models.CharField(
        _("Fax Number"),
        max_length=16,
        help_text=_('The fax number of the employee.'),
        validators=[],
        blank=True,
        null=True,
    )
    cell = models.CharField(
        _("Cell Number"),
        max_length=16,
        help_text=_('The cell number of the employee.'),
        db_index=True,
        validators=[],
        blank=True,
        null=True,
    )
    email = models.EmailField(
        _("Email"),
        help_text=_('The email of this employee.'),
        db_index=True,
        blank=True,
        null=True,
    )
    city = models.CharField(
        _("City"),
        max_length=31,
        help_text=_('The city this employee lives in.'),
        db_index=True,
    )
    province = models.CharField(
        _("Province"),
        max_length=15,
        help_text=_('The province this employee lives in.'),
        db_index=True,
        blank=True,
        null=True,
    )
    postal_code = models.CharField(
        _("Postal Code"),
        max_length=11,
        help_text=_('The postal code. For example, 94043.'),
        db_index=True,
        blank=True,
        null=True,
        validators=[],
    )
    ldn_area = models.CharField(
        _("London Area"),
        max_length=31,
        help_text=_('The area in London that this employee lives in.'),
        blank=True,
        null=True,
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
    #  SYSTEM FIELDS
    #

    user = models.OneToOneField(
        User,
        help_text=_('The user whom belongs to this employee.'),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_index=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    last_modified = models.DateTimeField(auto_now=True, db_index=True,)

    #
    #  FUNCTIONS
    #

    def __str__(self):
        if self.middle_name:
            return str(self.given_name)+" "+str(self.middle_name)+" "+str(self.last_name)
        else:
            return str(self.given_name)+" "+str(self.last_name)
