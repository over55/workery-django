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


def report_13_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    jobs = WorkOrder.objects.filter(
        assignment_date__range=(from_dt,to_dt),
        # associate__isnull=False
    ).order_by(
       '-id'
    ).prefetch_related(
        'customer',
        'associate',
        'skill_sets'
    )

    # Generate the CSV header row.
    rows = (["Job No.", "Associate", "Client", 'Skill Sets'],)

    # Generate hte CSV data.
    for job in jobs.all():

        # Get our list of skill sets.
        skill_set_text = job.get_skill_sets_string()

        # Generate the reason.
        rows += ([
            str(job.id),
            str(job.customer),
            str(job.associate),
            skill_set_text,
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="jobs.csv"'
    return response


def report_14_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    jobs = WorkOrder.objects.filter(
        completion_date__range=(from_dt,to_dt),
        customer__type_of=COMMERCIAL_JOB_TYPE_OF_ID,
        customer__isnull=False,
        associate__isnull=False
    ).order_by(
       '-id'
    ).prefetch_related(
        'customer',
        'associate',
        'skill_sets'
    )

    # Generate the CSV header row.
    rows = (["Job No.", "Completion date", "Associate", "Client", "WSIB Date", "Total Labour", "Invoice #", "Skill Sets"],)

    # Generate hte CSV data.
    for job in jobs.all():

        # Get our list of skill sets.
        skill_set_text = job.get_skill_sets_string()

        # Set the invoice ID.
        invoice_id = "-" if job.invoice_id is None else job.invoice_id
        invoice_id = "-" if job.invoice_id <= 0 else job.invoice_id
        wsib_insurance_date = "-" if job.associate.wsib_insurance_date is None else job.associate.wsib_insurance_date
        hours = "-" if job.hours <= 0 else job.hours

        # Generate the reason.
        rows += ([
            str(job.id),
            str(job.completion_date),
            str(job.associate),
            str(job.customer),
            str(wsib_insurance_date),
            str(hours),
            str(invoice_id),
            skill_set_text,
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="commercial_jobs.csv"'
    return response
