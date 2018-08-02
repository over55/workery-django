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


def report_10_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    jobs = WorkOrder.objects.filter(
        assignment_date__range=(from_dt,to_dt),
        # associate__isnull=False
    ).order_by(
       '-assignment_date'
    ).prefetch_related(
        'customer',
        'associate',
        'skill_sets'
    )

    # Convert our aware datetimes to the specific timezone of the tenant.
    today = timezone.now()
    tenant_today = request.tenant.to_tenant_dt(today)
    tenant_from_dt = request.tenant.to_tenant_dt(from_dt)
    tenant_from_dt = tenant_from_dt.date()
    tenant_to_dt = request.tenant.to_tenant_dt(to_dt)
    tenant_to_dt = tenant_to_dt.date()

    # Generate our new header.
    rows = (["Jobs Report","","",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"",],)
    rows += (["From Assignment Date:", pretty_dt_string(tenant_from_dt),"",],)
    rows += (["To Assignment Date:", pretty_dt_string(tenant_to_dt),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += (["Job No.", "Assignment Date", "Associate", "Client", 'Skill Sets'],)

    # Generate hte CSV data.
    for job in jobs.all():

        # Get our list of skill sets.
        skill_set_text = job.get_skill_sets_string()

        # Generate the reason.
        rows += ([
            str(job.id),
            pretty_dt_string(job.assignment_date),
            str(job.associate),
            str(job.customer),
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
