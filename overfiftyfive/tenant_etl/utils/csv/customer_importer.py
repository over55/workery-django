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
    SharedMe
)
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Customer,
    CustomerAffiliation,
    Organization
)
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
                home_phone = row[4]
                postal_code = row[5]
                job_info_read = row[6]
                learn_about = row[7]
                is_support = bool_or_none(row[8])
                is_senior = bool_or_none(row[9])
                birthdate = row[10]
                job_description = row[11]
                address = row[12]
                city = row[13]
                email = row[14]
                url = None
                telephone_extension = None

                # Minor formatting.
                email = email.replace(';', '')
                email = email.replace(':', '')
                email = email.replace('NONE', '')
                email = email.replace('N/A', '')
                email = email.replace(' ', '')
                email = email.lower()
                address = '-' if address is '' else address
                address = '-' if address is None else address
                city = "London" if city is '' else city
                if "www" in email.lower():
                    url = "http://"+email.lower()
                    email = ""
                if "ext" in email.lower():
                    telephone_extension = email
                    email = ""
                home_phone = home_phone.replace('(', '')
                home_phone = home_phone.replace(')', '')
                home_phone = home_phone.replace('-', '')
                home_phone = home_phone.replace(' ', '')
                home_phone = home_phone.replace('.', '')
                home_phone = int_or_none(home_phone)

                # Convert the datetime.
                local_birthdate = get_utc_dt_from_toronto_dt_string(birthdate)
                local_project_date = get_utc_dt_from_toronto_dt_string(project_date)

                # Attempt to lookup or create user.
                user = User.objects.filter(email=email).first()
                if user is None:
                    # Create our user.
                    user = User.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        username=get_unique_username_from_email(email),
                        is_active=True,
                    )

                    # Generate and assign the password.
                    user.set_password(get_random_string())
                    user.save()

                    # Attach our user to the "CUSTOMER_GROUP_ID"
                    user.groups.add(CUSTOMER_GROUP_ID)

                # Insert our extracted data into our database.
                customer, create = Customer.objects.update_or_create(
                    id=int_or_none(pk),
                    defaults={
                        'id':int_or_none(pk),
                        'owner': user,
                        'last_name':last_name,
                        'given_name':first_name,
                        # 'middle_name':middle_name,
                        'telephone': home_phone,
                        'telephone_extension': telephone_extension,
                        'postal_code': postal_code,
                        'birthdate': local_birthdate,
                        'street_address': address,
                        'address_locality': city,
                        'address_country': 'Canada',
                        'address_region': 'Ontario',
                        'email': email,
                        'join_date': local_project_date,
                        'job_info_read': job_info_read,
                        'how_hear': learn_about,
                        'description': job_description,
                        'is_senior': bool(is_senior),
                        'is_support': bool(is_support)
                    }
                )

            except Exception as e:
                print(e)
                print(row)
                print()


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
                url = None

                # Minor formatting.
                email = email.replace(';', '')
                email = email.lower()
                address = '-' if address is '' else address
                address = '-' if address is None else address
                city = "London" if city is '' else city
                if "www" in email.lower():
                    url = "http://"+email.lower()
                    email = ""
                phone = phone.replace('(', '')
                phone = phone.replace(')', '')
                phone = phone.replace('-', '')
                phone = phone.replace(' ', '')
                phone = phone.replace('.', '')
                phone = int_or_none(phone)
                fax = fax.replace('(', '')
                fax = fax.replace(')', '')
                fax = fax.replace('-', '')
                fax = fax.replace(' ', '')
                fax = fax.replace('.', '')
                fax = int_or_none(fax)

                # Attempt to lookup or create user.
                user = User.objects.filter(email=email).first()
                if user is None:
                    # Create our user.
                    user = User.objects.create(
                        first_name='-',
                        last_name='-',
                        email=email,
                        username=get_unique_username_from_email(email),
                        is_active=True,
                    )

                    # Generate and assign the password.
                    user.set_password(get_random_string())
                    user.save()

                    # Attach our user to the "CUSTOMER_GROUP_ID"
                    user.groups.add(CUSTOMER_GROUP_ID)

                # Insert our extracted data into our database.
                customer, create = Customer.objects.update_or_create(
                    id=int_or_none(pk),
                    defaults={
                        'id':int_or_none(pk),
                        'owner': user,
                        'name':caller,
                        'telephone': phone,
                        'postal_code': postal_code,
                        'street_address': address,
                        'address_locality': city,
                        'address_country': 'Canada',
                        'address_region': 'Ontario',
                        'email': email,
                        'fax_number': fax,
                        'description': com1,
                        'url': url
                    }
                )

            except Exception as e:
                print(e)
                print(row)
                print()

            # If company name does not already exist then create our company now.
            if not Organization.objects.filter(name=company).exists():
                organization = Organization.objects.create(name=company)
                CustomerAffiliation.objects.create(
                    customer=customer,
                    organization=organization,
                    type_of=AFFILIATION_TYPE_AFFILIATION_ID
                )
