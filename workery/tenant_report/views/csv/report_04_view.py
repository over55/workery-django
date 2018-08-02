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


def report_04_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    cancelled_jobs = WorkOrder.objects.filter(
        Q(completion_date__range=(from_dt,to_dt)) &
        Q(
            Q(state=WORK_ORDER_STATE.CANCELLED) |
            Q(state=WORK_ORDER_STATE.DECLINED)
        ) &
        Q(associate__isnull=False)
    ).order_by(
        '-completion_date'
    ).prefetch_related(
        'customer',
        'associate',
        'skill_sets'
    )

    # Convert our aware datetimes to the specific timezone of the tenant.
    today = timezone.now()
    today = request.tenant.to_tenant_dt(today)
    from_dt = request.tenant.to_tenant_dt(from_dt)
    from_dt = from_dt.date()
    to_dt = request.tenant.to_tenant_dt(to_dt)
    to_dt = to_dt.date()

    # Generate our new header.
    rows = (["Cancelled Jobs Report","","","","","",],)
    rows += (["Report Date:", pretty_dt_string(today),"","","","",],)
    rows += (["From Assignment Date:", pretty_dt_string(from_dt),"","","","",],)
    rows += (["To Assignment Date:", pretty_dt_string(to_dt),"","","","",],)
    rows += (["","","","","","",],)
    rows += (["","","","","","",],)

    # Generate the CSV header row.
    rows += (["Job No.", "Date", "Reason", "Associate No.", "Associate Name", "Skill Set(s)"],)

    # Generate hte CSV data.
    for cancelled_job in cancelled_jobs.all():

        # Generate the closing reason.
        closing_reason = cancelled_job.pretty_closing_reason()

        # Attach all the skill sets that are associated with each job.
        skill_set_string = cancelled_job.get_skill_sets_string()

        # Minor defensive code.
        associate = cancelled_job.associate
        associate_id = '-' if associate is None else associate.id
        associate = '-' if associate is None else associate
        closing_reason = '-' if closing_reason is None else closing_reason
        skill_set_string = "-" if len(skill_set_string) is 0 else skill_set_string

        # Generate the reason.
        rows += ([
            str(cancelled_job.id),
            pretty_dt_string(cancelled_job.completion_date),
            str(closing_reason),
            str(associate_id),
            str(associate),
            skill_set_string
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="job_cancellation_reasons.csv"'
    return response
