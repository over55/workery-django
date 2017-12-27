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
from tenant_foundation.models import Staff
from tenant_foundation.utils import *


def run_staff_importer_from_csv_file(csvfile):
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
