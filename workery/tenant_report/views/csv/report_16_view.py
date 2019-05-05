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
    Customer,
    Staff,
    Partner
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


def client_report(aware_now_d, aware_from_d, aware_to_d):
    customers = Customer.objects.filter(
        join_date__range=(aware_from_d,aware_to_d),
        how_hear__isnull=False
    ).order_by(
       '-join_date'
    )

    # Generate our new header.
    rows = (["How Client Finds Us (Long) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Client No.",
        "First Name",
        "Last Name",
        "Join Date",
        "How Did You Heard About Us?",
        "Other"
    ],)

    # Generate hte CSV data.
    for customer in customers.iterator(chunk_size=200):

        how_hear_other = "-"
        if customer.how_hear.id == 1:
            how_hear_other = customer.how_hear_other

        # Generate the reason.
        rows += ([
            str(customer.id),
            customer.given_name,
            customer.last_name,
            pretty_dt_string(customer.join_date),
            str(customer.how_hear.text),
            str(how_hear_other),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_clients_finds_us_long_report.csv"'
    return response


def associate_report(aware_now_d, aware_from_d, aware_to_d):
    associates = Associate.objects.filter(
        join_date__range=(aware_from_d,aware_to_d),
        how_hear__isnull=False
    ).order_by(
       '-join_date'
    )

    # Generate our new header.
    rows = (["How Associates Finds Us (Long) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Associate No.",
        "First Name",
        "Last Name",
        "Join Date",
        "How Did You Heard About Us?",
        "Other"
    ],)

    # Generate hte CSV data.
    for associate in associates.iterator(chunk_size=200):

        how_hear_other = "-"
        if associate.how_hear.id == 1:
            how_hear_other = associate.how_hear_other

        # Generate the reason.
        rows += ([
            str(associate.id),
            associate.given_name,
            associate.last_name,
            pretty_dt_string(associate.join_date),
            str(associate.how_hear.text),
            str(how_hear_other),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_associates_finds_us_long_report.csv"'
    return response

def staff_report(aware_now_d, aware_from_d, aware_to_d):
    staves = Staff.objects.filter(
        join_date__range=(aware_from_d,aware_to_d),
        how_hear__isnull=False
    ).order_by(
       '-join_date'
    )

    # Generate our new header.
    rows = (["How Staff Finds Us (Long) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Staff No.",
        "First Name",
        "Last Name",
        "Join Date",
        "How Did You Heard About Us?",
        "Other"
    ],)

    # Generate hte CSV data.
    for staff in staves.iterator(chunk_size=200):

        how_hear_other = "-"
        if staff.how_hear.id == 1:
            how_hear_other = staff.how_hear_other

        # Generate the reason.
        rows += ([
            str(staff.id),
            staff.given_name,
            staff.last_name,
            pretty_dt_string(staff.join_date),
            str(staff.how_hear.text),
            str(how_hear_other),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_staff_finds_us_long_report.csv"'
    return response

def partner_report(aware_now_d, aware_from_d, aware_to_d):
    partners = Partner.objects.filter(
        join_date__range=(aware_from_d,aware_to_d),
        how_hear__isnull=False
    ).order_by(
       '-join_date'
    )

    # Generate our new header.
    rows = (["How Partner Finds Us (Long) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Partner No.",
        "First Name",
        "Last Name",
        "Join Date",
        "How Did You Heard About Us?",
        "Other"
    ],)

    # Generate hte CSV data.
    for partner in partners.iterator(chunk_size=200):

        how_hear_other = "-"
        if partner.how_hear.id == 1:
            how_hear_other = partner.how_hear_other

        # Generate the reason.
        rows += ([
            str(partner.id),
            partner.given_name,
            partner.last_name,
            pretty_dt_string(partner.join_date),
            str(partner.how_hear.text),
            str(how_hear_other),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_partners_finds_us_long_report.csv"'
    return response

def report_16_streaming_csv_view(request):
    # Get our user parameters.
    naive_from_dt = request.GET.get('from_dt', None)
    naive_to_dt = request.GET.get('to_dt', None)
    user_type = request.GET.get('user_type', None)

    # Convert our datatime `string` into a `datatime` object.
    naive_from_dt = parser.parse(naive_from_dt)
    naive_to_dt = parser.parse(naive_to_dt)

    # Convert our aware datetimes to the specific timezone of the tenant.
    today = timezone.now()
    tenant_today_dt = request.tenant.to_tenant_dt(today)
    tenant_today_d = tenant_today_dt.date()
    tenant_from_dt = request.tenant.localize_tenant_dt(naive_from_dt)
    tenant_from_d = tenant_from_dt.date()
    tenant_to_dt = request.tenant.localize_tenant_dt(naive_to_dt)
    tenant_to_d = tenant_to_dt.date()

    if user_type == "client":
        return client_report(tenant_today_d, tenant_from_d, tenant_to_d)

    if user_type == "associate":
        return associate_report(tenant_today_d, tenant_from_d, tenant_to_d)

    if user_type == "staff":
        return staff_report(tenant_today_d, tenant_from_d, tenant_to_d)

    if user_type == "partner":
        return partner_report(tenant_today_d, tenant_from_d, tenant_to_d)
