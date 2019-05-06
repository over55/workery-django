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
    Partner,
    HowHearAboutUsItem
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
    items = HowHearAboutUsItem.objects.filter(is_for_customer=True).order_by('sort_number')

    # Generate our new header.
    rows = (["How Client Finds Us (Short) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Description",
        "Count"
    ],)

    # Iterate through all the items.
    for item in items.all():
        count = item.customers.filter(
            join_date__range=(aware_from_d,aware_to_d),
            how_hear__isnull=False
        ).count()

        # Generate the reason.
        rows += ([
            item.text,
            str(count),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_clients_finds_us_short_report.csv"'
    return response

def associate_report(aware_now_d, aware_from_d, aware_to_d):
    items = HowHearAboutUsItem.objects.filter(is_for_associate=True).order_by('sort_number')

    # Generate our new header.
    rows = (["How Associates Finds Us (Short) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Description",
        "Count"
    ],)

    # Iterate through all the items.
    for item in items.all():
        count = item.associates.filter(
            join_date__range=(aware_from_d,aware_to_d),
            how_hear__isnull=False
        ).count()

        # Generate the reason.
        rows += ([
            item.text,
            str(count),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_associates_finds_us_short_report.csv"'
    return response

def staff_report(aware_now_d, aware_from_d, aware_to_d):
    items = HowHearAboutUsItem.objects.filter(is_for_staff=True).order_by('sort_number')

    # Generate our new header.
    rows = (["How Staff Finds Us (Short) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Description",
        "Count"
    ],)

    # Iterate through all the items.
    for item in items.all():
        count = item.staves.filter(
            join_date__range=(aware_from_d,aware_to_d),
            how_hear__isnull=False
        ).count()

        # Generate the reason.
        rows += ([
            item.text,
            str(count),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_staff_finds_us_short_report.csv"'
    return response

def partner_report(aware_now_d, aware_from_d, aware_to_d):
    items = HowHearAboutUsItem.objects.filter(is_for_partner=True).order_by('sort_number')

    # Generate our new header.
    rows = (["How Partners Finds Us (Short) Report","","",],)
    rows += (["Report Date:", pretty_dt_string(aware_now_d),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(aware_from_d),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(aware_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Description",
        "Count"
    ],)

    # Iterate through all the items.
    for item in items.all():
        count = item.partners.filter(
            join_date__range=(aware_from_d,aware_to_d),
            how_hear__isnull=False
        ).count()

        # Generate the reason.
        rows += ([
            item.text,
            str(count),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="how_partners_finds_us_short_report.csv"'
    return response

def report_17_streaming_csv_view(request):
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
