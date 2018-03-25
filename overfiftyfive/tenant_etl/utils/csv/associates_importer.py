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
    get_unique_username_from_email,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.constants import *
from shared_foundation.models import (
    SharedFranchise,
    SharedUser
)
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Associate,
    AssociateAffiliation
)
from tenant_foundation.utils import *


def run_associates_importer_from_csv_file(csvfile):
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

            # Minor formatting.
            email = email.replace(';', '')
            email = email.replace(':', '')
            email = email.replace('NONE', '')
            email = email.replace('N/A', '')
            email = email.replace(' ', '')
            email = email.lower()
            address = '-' if address is '' else address
            address = '-' if address is None else address
            province = 'ON' if province is '' else province
            province = 'ON' if province is None else province
            city = "London" if city is '' else city
            fax = fax.replace('(', '')
            fax = fax.replace(')', '')
            fax = fax.replace('-', '')
            fax = fax.replace(' ', '')
            fax = fax.replace('.', '')

            phone = phone.replace('(', '')
            phone = phone.replace(')', '')
            phone = phone.replace('-', '')
            phone = phone.replace(' ', '')
            phone = phone.replace('.', '')

            cell = cell.replace('(', '')
            cell = cell.replace(')', '')
            cell = cell.replace('-', '')
            cell = cell.replace(' ', '')
            cell = cell.replace('.', '')

            # Attempt to lookup or create user.
            user = User.objects.filter(email=email).first()
            if user is None:
                # Create our user.
                user = User.objects.create(
                    first_name=given_name,
                    last_name=last_name,
                    email=email,
                    username=get_unique_username_from_email(email),
                    is_active=True,
                )

                # Generate and assign the password.
                user.set_password(get_random_string())
                user.save()

                # Attach our user to the "Executive"
                user.groups.add(ASSOCIATE_GROUP_ID)

            # Create or update.
            try:
                associate, create = Associate.objects.update_or_create(
                    id=int_or_none(pk),
                    defaults={
                        'id':int_or_none(pk),
                        'owner': user,
                        'last_name':last_name,
                        'given_name':given_name,
                        'business':business,
                        'middle_name':middle_name,
                        # 'is_active':bool_or_none(is_active),
                        'birthdate':local_birthdate,
                        'address_country':'Canada',
                        'join_date':local_join_date,
                        'telephone':phone,
                        'mobile':cell,
                        'fax_number':fax,
                        'email':email,
                        'address_locality':city,
                        'address_region':province,
                        'street_address': address,
                        'postal_code':postal_code,
                        'area_served':ldn_area,
                        'hourly_salary_desired':int_or_none(hourly_salary_desired),
                        'limit_special':limit_special,
                        'dues_pd':local_dues_pd,
                        'ins_due':local_ins_due,
                        'police_check':local_police_check,
                        'drivers_license_class':drivers_license_class,
                        'comments':comments,
                        'has_car':bool_or_none(has_van),
                        'has_van':bool_or_none(has_van),
                        'has_truck':bool_or_none(has_truck),
                        'is_full_time':bool_or_none(is_full_time),
                        'is_part_time':bool_or_none(is_part_time),
                        'is_contract_time':bool_or_none(is_contract_time),
                        'is_small_job':bool_or_none(is_small_job),
                        'how_hear':how_hear
                    }
                )

                # For debugging purposes.
                # print(associate, create)
            except Exception as e:
                print(e)
                print(row)
                print()
