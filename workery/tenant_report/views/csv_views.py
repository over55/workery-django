# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Extract
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    Order,
    TaskItem
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


def report_07_streaming_csv_view(request):
    today = datetime.datetime.today()
    associates = Associate.objects.filter(
        Q(owner__is_active=True) &
        ~Q(commercial_insurance_expiry_date=None) &
        Q(commercial_insurance_expiry_date__gte=today)
    ).order_by('-commercial_insurance_expiry_date')

    # Generate the CSV header row.
    rows = (["ID #", "Name", "Commerical Insurance Due Dates"],)

    # Generate hte CSV data.
    for associate in associates.all():
        rows += ([
            associate.id,
            str(associate),
            "-" if associate.commercial_insurance_expiry_date is None else associate.commercial_insurance_expiry_date
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="associate_commercial_insurance_due_dates.csv"'
    return response


def report_08_streaming_csv_view(request):
    today = datetime.datetime.today()
    associates = Associate.objects.filter(
        Q(owner__is_active=True) &
        ~Q(police_check=None) &
        Q(police_check__gte=today)
    ).order_by('-police_check')

    # Generate the CSV header row.
    rows = (["ID #", "Name", "Commerical Insurance Due Dates"],)

    # Generate hte CSV data.
    for associate in associates.all():
        rows += ([
            associate.id,
            str(associate),
            "-" if associate.police_check is None else associate.police_check
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="associate_policy_check_due_dates.csv"'
    return response


def report_09_streaming_csv_view(request):
    # DEVELOPERS NOTE:
    # - We will sort by the month and day of the associate's birthdate.
    associates = Associate.objects.annotate(
        month=Extract('birthdate', 'month'),
        day=Extract('birthdate', 'day')
    ).filter(
        owner__is_active=True
    ).order_by('month', 'day')

    # Generate the CSV header row.
    rows = (["ID #", "Name", "Birthday"],)

    # Generate hte CSV data.
    for associate in associates.all():
        rows += ([
            associate.id,
            str(associate),
            "-" if associate.birthdate is None else associate.birthdate
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="associate_birthdays.csv"'
    return response
