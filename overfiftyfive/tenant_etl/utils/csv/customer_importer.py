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
from tenant_foundation.models import Customer
from tenant_foundation.models.organization import Organization
from tenant_foundation.utils import *


def run_customer_importer_from_csv_file(csvfile):
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for i, row in enumerate(csvreader):
        if i > 0:
            try:
                # For debugging purposes.
                # print(row)

                # Fetch our values.
                pk = int_or_none(row[0])
                project_date = row[1]
                last_name = row[2]
                first_name = row[3]
                home_phone = int_or_none(row[4])
                postal_code = row[5]
                job_info_read = row[6]
                learn_about = row[7]
                is_suppert = bool_or_none(row[8])
                is_senior = bool_or_none(row[9])
                birthdate = row[10]
                job_description = row[11]
                address = row[12]
                city = row[13]
                email = row[14]

            except Exception as e:
                print(e)

            # Convert the datetime.
            local_birthdate = get_utc_dt_from_toronto_dt_string(birthdate)
            local_project_date = get_utc_dt_from_toronto_dt_string(project_date)

            # Insert our extracted data into our database.
            customer, create = Customer.objects.update_or_create(
                id=int_or_none(pk),
                defaults={
                    'id':int_or_none(pk),
                    'last_name':last_name,
                    'given_name':first_name,
                    # 'middle_name':middle_name,
                    'telephone': home_phone,
                    'postal_code': postal_code,
                    'birthdate': local_birthdate,
                    'street_address': address,
                    'address_locality': city,
                    'address_country': 'Canada',
                    'email': email,
                    'join_date': local_project_date,
                    'job_info_read': job_info_read,
                    'how_hear': learn_about,
                    'description': job_description,
                    'is_senior': bool(is_senior),
                    'is_suppert': bool(is_suppert)
                }
            )


def run_customer_and_org_importer_from_csv_file(csvfile):
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for i, row in enumerate(csvreader):
        if i > 0:
            try:
                # For debugging purposes.
                # print(row)

                pk = row[0]
                caller = row[1]
                company = row[2] #TODO
                pick = bool_or_none(row[3]) #TODO: ???
                phone = row[4]
                address = row[5]
                city = row[6]
                postal_code = row[7]
                fax = row[8]
                email = row[9]
                com1 = row[10]

                # Insert our extracted data into our database.
                customer, create = Customer.objects.update_or_create(
                    id=int_or_none(pk),
                    defaults={
                        'id':int_or_none(pk),
                        'name':caller,
                        'telephone': phone,
                        'postal_code': postal_code,
                        'street_address': address,
                        'address_locality': city,
                        'address_country': 'Canada',
                        'email': email,
                        'fax_number': fax,
                        'description': com1,
                    }
                )

            except Exception as e:
                print(e)

            # If company name does not already exist then create our company now.
            if not Organization.objects.filter(name=company).exists():
                org = Organization.objects.create(name=company)
