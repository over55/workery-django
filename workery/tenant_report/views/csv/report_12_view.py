# -*- coding: utf-8 -*-
import datetime
from dateutil import parser
from djmoney.money import Money
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Extract
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from shared_foundation.constants import *
from shared_foundation.mixins import ExtraRequestProcessingMixin
from shared_foundation.utils import *
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    WORK_ORDER_STATE,
    WorkOrder,
    TaskItem,
    SkillSet
)

"""
Code below was taken from:
https://docs.djangoproject.com/en/2.0/howto/outputting-csv/
"""

import csv
from django.http import StreamingHttpResponse

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def report_09_streaming_csv_view(request):
    # DEVELOPERS NOTE:
    # - We will sort by the month and day of the associate's birthdate.
    customers = Customer.objects.all().order_by('last_name', 'given_name', ).prefetch_related(
        'owner'
    )

    # Convert our aware datetimes to the specific timezone of the tenant.
    today = timezone.now()
    tenant_today = request.tenant.to_tenant_dt(today)

    # Generate our new header.
    rows = (["Customer Report","", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today), "", "", "", "", "", "", "", "", "", "", "", "", "", "",],)
    rows += (["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",],)
    rows += (["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",],)

    # Generate the CSV header row.
    rows += ([
        "Customer No.",
        "Name",
        "Type",
        "Status",
        "Ok to email?",
        "Ok to text?",
        "Address",
        "Address (Extra)",
        "City",
        "Province",
        "Country",
        "Postal",
        'Email',
        'Telephone',
        'Telephone Type',
        'Telephone Extension',
        'Other Telephone',
        'Other Telephone Type',
        'Other Telephone Extension',
    ],)

    type_of_choices = dict(CUSTOMER_TYPE_OF_CHOICES)

    tele_type_of_choices = dict(TELEPHONE_CONTACT_POINT_TYPE_OF_CHOICES)

    # Generate hte CSV data.
    for customer in customers.all():

        customer_type_of = type_of_choices[customer.type_of]
        telephone_type_of = tele_type_of_choices[customer.telephone_type_of]
        other_telephone_type_of = tele_type_of_choices[customer.other_telephone_type_of]

        rows += ([
            customer.id,
            customer.last_name+", "+customer.given_name,
            customer_type_of,
            customer.get_pretty_status(),
            customer.is_ok_to_email,
            customer.is_ok_to_text,
            customer.street_address,
            customer.street_address_extra,
            customer.address_locality,
            customer.address_region,
            customer.address_country,
            customer.postal_code,
            customer.email,
            customer.telephone,
            telephone_type_of,
            customer.telephone_extension,
            customer.other_telephone,
            other_telephone_type_of,
            customer.other_telephone_extension
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    return response
