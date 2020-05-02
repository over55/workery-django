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


def report_19_streaming_csv_view(request):
    # Get our user parameters.
    naive_from_dt = request.GET.get('from_dt', None)
    naive_to_dt = request.GET.get('to_dt', None)
    state = request.GET.get('state', 'all')
    tag_ids = request.GET.get('tag_ids', None)

    tag_ids_arr = tag_ids.split(",")
    for idx, val in enumerate(tag_ids_arr):
        tag_ids_arr[idx] = int(val)

    # Convert our datatime `string` into a `datatime` object.
    naive_from_dt = parser.parse(naive_from_dt)
    naive_to_dt = parser.parse(naive_to_dt)

    # Convert our aware datetimes to the specific timezone of the tenant.
    today = timezone.now()
    today = request.tenant.to_tenant_dt(today)
    from_dt = request.tenant.localize_tenant_dt(naive_from_dt)
    from_d = from_dt.date()
    to_dt = request.tenant.localize_tenant_dt(naive_to_dt)
    to_d = to_dt.date()

    # Run our filter lookup.
    queryset = None
    if state == 'all':
        queryset = WorkOrder.objects.filter(
            Q(tags__in=tag_ids_arr) &
            Q(assignment_date__range=(from_dt,to_dt))
        ).order_by(
            '-assignment_date'
        ).prefetch_related(
            'customer',
            'associate',
            'tags'
        )
    else:
        queryset = WorkOrder.objects.filter(
            Q(tags__in=tag_ids_arr) &
            Q(state=state) &
            Q(assignment_date__range=(from_dt,to_dt))
        ).order_by(
            '-assignment_date'
        ).prefetch_related(
            'customer',
            'associate',
            'tags'
        )

    # Defensive Code: If nothing is found then return nothing.
    if queryset.count() == 0:
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            content_type="text/csv"
        )
        response['Content-Disposition'] = 'attachment; filename="job_tags.csv"'
        return response

    # Generate our new header.
    rows = (["Job Tags Report","","","","","","","","","",],)
    rows += (["Report Date:", pretty_dt_string(today),"","","","","","","","",],)
    rows += (["From Assignment Date:", pretty_dt_string(from_d),"","","","","","","","",],)
    rows += (["To Assignment Date:", pretty_dt_string(to_d),"","","","","","","","",],)
    rows += (["Job Status:", str(state),"","","","","","","","",],)
    # rows += (["Skill Set(s):", str(state),"","","","","","","","",],)
    rows += (["","","","","","","","","","",],)
    rows += (["","","","","","","","","","",],)

    # Generate the CSV header row.
    rows += ([
        # "Job No.",
        "Assignment Date",
        "Associate No.",
        "Associate Name",
        "Job Completion Date",
        "Job #",
        "Job Status",
        "Client No.",
        "Client Name",
        "Tags",
    ],)

    # Generate hte CSV data.
    for job in queryset.iterator(chunk_size=100):
        # Get the type of job from a "tuple" object.
        test = dict(JOB_TYPE_OF_CHOICES)
        job_type = test[job.type_of]

        # Attach all the tags that are associated with each job.
        tag_string = job.get_tags_string()

        customer_telephone = job.customer.telephone if job.customer else "-"
        customer_email = job.customer.email if job.customer else "-"
        associate_email = job.associate.email if job.associate else "-"

        # Generate the row.
        rows += ([
            pretty_dt_string(job.assignment_date),
            str(job.associate.id),
            str(job.associate),
            pretty_dt_string(job.completion_date),
            str(job.id),
            job.get_pretty_status(),
            str(job.customer.id),
            str(job.customer),
            tag_string,
            # job.customer.get_postal_address_without_postal_code(),
            # str(customer_telephone),
            # str(customer_email),
            # tag_string,
            # str(customer_telephone),
            # str(associate_email),
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="job_tags.csv"'
    return response
