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


def get_expiry_date(days=2):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


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

    def create_from_csvfile(self, csvfile):
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(csvreader):
            if i > 0:
                # For debugging purposes.
                # print(row)

                # Extract the data.
                pk = row[0]                     # CLIENTNO
                last_name = row[1]              # LNAME
                given_name = row[2]             # GNAMES
                business = row[3]               # BUSINESS
                middle_name = row[4]            # MNAME
                is_active = row[5]              # ACTIVE?
                birthdate = row[6]              # BIRTHDATE
                address = row[7]                # ADDRESS
                join_date = row[8]              # DATE
                phone = row[9]                  # PHONE
                fax = row[10]                   # FAX
                cell = row[11]                  # CELL
                email = row[12]                 # E-MAIL
                city = row[13]                  # CITY
                province = row[14]              # PROV
                postal_code = row[15]           # POSTCODE
                ldn_area = row[16]              # LONDAREA
                hourly_salary_desired = row[17] # HRLYSALDESIR
                limit_special = row[18]         # LIMITSPECIAL
                dues_pd = row[19]               # DUES PD
                ins_due = row[20]               # INS DUE
                police_check = row[21]          # POLCHK
                drivers_license_class = row[22] # DRLICCLASS
                comments = row[23]              # COMMENTS
                has_car = row[24]               # Car?
                has_van = row[25]               # Van?
                has_truck = row[26]             # Truck?
                is_full_time = row[27]          # Full Time
                is_part_time = row[28]          # Part Time
                is_contract_time = row[29]      # Contract
                is_small_job = row[30]          # Small Jobs
                how_hear = row[31]              # How Hear

                # Convert the datetime.
                local_birthdate = get_dt_from_toronto_timezone_ms_access_dt_string(birthdate)
                local_join_date = get_dt_from_toronto_timezone_ms_access_dt_string(join_date)
                local_dues_pd = get_dt_from_toronto_timezone_ms_access_dt_string(dues_pd)
                local_ins_due = get_dt_from_toronto_timezone_ms_access_dt_string(ins_due)
                local_police_check = get_dt_from_toronto_timezone_ms_access_dt_string(police_check)

                try:
                    # Fetch
                    employee = Staff.objects.get(pk=int_or_none(pk))

                    # Update
                    employee.last_name=last_name
                    employee.last_name=last_name
                    employee.given_name=given_name
                    employee.business=business
                    employee.middle_name=middle_name
                    employee.is_active = bool_or_none(is_active)
                    employee.birthdate = local_birthdate
                    employee.address = address
                    employee.join_date = local_join_date
                    employee.phone = phone
                    employee.fax = fax
                    employee.cell = cell
                    employee.email = email
                    employee.city = city
                    employee.province = province
                    employee.postal_code = postal_code
                    employee.ldn_area = ldn_area
                    employee.hourly_salary_desired = int_or_none(hourly_salary_desired)
                    employee.limit_special = limit_special
                    employee.dues_pd = local_dues_pd
                    employee.ins_due = local_ins_due
                    employee.police_check = local_police_check
                    employee.drivers_license_class = drivers_license_class,
                    employee.comments = comments
                    employee.has_car = bool_or_none(has_car)
                    employee.has_van = bool_or_none(has_van)
                    employee.has_truck = bool_or_none(has_truck)
                    employee.is_full_time = bool_or_none(is_full_time)
                    employee.is_part_time = bool_or_none(is_part_time)
                    employee.is_contract_time = bool_or_none(is_contract_time)
                    employee.is_small_job = bool_or_none(is_small_job)
                    employee.how_hear = how_hear
                    employee.save

                except Staff.DoesNotExist:
                    # Create
                    Staff.objects.create(
                        pk=int_or_none(pk),
                        last_name=last_name,
                        given_name=given_name,
                        business=business,
                        middle_name=middle_name,
                        is_active=bool_or_none(is_active),
                        birthdate=local_birthdate,
                        address=address,
                        join_date=local_join_date,
                        phone=phone,
                        cell=cell,
                        fax=fax,
                        email=email,
                        city=city,
                        province=province,
                        postal_code=postal_code,
                        ldn_area=ldn_area,
                        hourly_salary_desired=int_or_none(hourly_salary_desired),
                        limit_special=limit_special,
                        dues_pd=local_dues_pd,
                        ins_due=local_ins_due,
                        police_check=local_police_check,
                        drivers_license_class=drivers_license_class,
                        comments=comments,
                        has_car=bool_or_none(has_van),
                        has_van=bool_or_none(has_van),
                        has_truck=bool_or_none(has_truck),
                        is_full_time=bool_or_none(is_full_time),
                        is_part_time=bool_or_none(is_part_time),
                        is_contract_time=bool_or_none(is_contract_time),
                        is_small_job=bool_or_none(is_small_job),
                        how_hear=how_hear
                    )


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
