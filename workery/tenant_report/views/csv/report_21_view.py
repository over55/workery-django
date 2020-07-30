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
    SkillSet,
    Partner,
    Staff
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


def report_21_streaming_csv_view(request):
    today = timezone.now()
    associates = Associate.objects.filter(
        Q(owner__is_active=True)
    )
    customers = Customer.objects.filter(
        Q(owner__is_active=True)
    )
    partners = Partner.objects.filter(
        Q(owner__is_active=True)
    )
    staves = Staff.objects.filter(
        Q(owner__is_active=True)
    )

    # Convert our aware datetimes to the specific timezone of the tenant.
    tenant_today = request.tenant.to_tenant_dt(today)

    # Generate our new header.
    rows = (["Market Emails","","","",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"", "",],)
    rows += (["", "", "", "",],)
    rows += (["", "", "", "",],)

    # Generate the CSV header row.
    rows += ([
        "No.",
        "Name",
        "Type",
        "Email"
    ],)

    # Generate the CSV dataset.
    for associate in associates.filter(Q(is_ok_to_email=True)&~Q(email=None)):

        # Generate our row.
        rows += ([
            associate.id,
            str(associate),
            "Associate",
            associate.email
        ],)

    # Generate the CSV dataset.
    for customer in customers.filter(Q(is_ok_to_email=True)&~Q(email=None)):

        # Generate our row.
        rows += ([
            customer.id,
            str(customer),
            "Customer",
            customer.email
        ],)

    # Generate the CSV dataset.
    for partner in partners.filter(Q(is_ok_to_email=True)&~Q(email=None)):

        # Generate our row.
        rows += ([
            partner.id,
            str(partner),
            "Partner",
            partner.email
        ],)

    # Generate the CSV dataset.
    for staff in staves.filter(~Q(email=None)):

        # Generate our row.
        rows += ([
            staff.id,
            str(staff),
            "Staff",
            staff.email
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="marketing_emails.csv"'
    return response
