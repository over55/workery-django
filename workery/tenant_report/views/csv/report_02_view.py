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


def report_02_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)
    state = request.GET.get('state', 'all')
    associate_id = request.GET.get('associate_id', None)
    associate = Associate.objects.filter(id=associate_id).first()

    # Defensive Code: If nothing is found then return nothing.
    if associate_id is None:
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            content_type="text/csv"
        )
        response['Content-Disposition'] = 'attachment; filename="associate_jobs.csv"'
        return response

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    jobs = None
    if state == 'all':
        jobs = WorkOrder.objects.filter(
            Q(associate=associate) &
            Q(assignment_date__range=(from_dt,to_dt))
        ).order_by(
            '-assignment_date'
        ).prefetch_related(
            'customer',
            'associate',
            'skill_sets'
        )
    else:
        jobs = WorkOrder.objects.filter(
            Q(associate=associate) &
            Q(state=state) &
            Q(assignment_date__range=(from_dt,to_dt))
        ).order_by(
            '-assignment_date'
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
    rows = (["Associate Jobs Report","","","","","","","","","",],)
    rows += (["Report Date:", pretty_dt_string(today),"","","","","","","","",],)
    rows += (["From Assignment Date:", pretty_dt_string(from_dt),"","","","","","","","",],)
    rows += (["To Assignment Date:", pretty_dt_string(to_dt),"","","","","","","","",],)
    rows += (["Associate Name:", str(associate),"","","","","","","","",],)
    rows += (["Associate No.:", str(associate.id),"","","","","","","","",],)
    rows += (["","","","","","","","","","",],)
    rows += (["","","","","","","","","","",],)

    # Generate the CSV header row.
    rows += ([
        "Job No.",
        "Assignment Date",
        "Job Completion Date",
        "Service Fee",
        "Job Labour",
        "Job Type",
        "Job Status",
        "Client No.",
        "Client Name",
        "Skill Set(s)",
        "Was survey conducted",
        "Was job satisfactory",
        "Was job finished on time and on budget",
        "Was associate punctual",
        "Was associate professional",
        "Would customer refer our organization",
        "Score"
    ],)

    # Generate hte CSV data.
    for job in jobs.all():
        # Get the type of job from a "tuple" object.
        test = dict(JOB_TYPE_OF_CHOICES)
        job_type = test[job.type_of]

        # Attach all the skill sets that are associated with each job.
        skill_set_string = job.get_skill_sets_string()

        # Format labour amount
        invoice_labour_amount = str(job.invoice_labour_amount)
        invoice_labour_amount = invoice_labour_amount.replace('C', '')

        # Format service fee.
        invoice_service_fee_amount = str(job.invoice_service_fee_amount)
        invoice_service_fee_amount = invoice_service_fee_amount.replace('C', '')

        # Set to empty.
        was_survey_conducted = 0
        was_job_satisfactory = '-'
        was_job_finished_on_time_and_on_budget = '-'
        was_associate_punctual = '-'
        was_associate_professional = '-'
        would_customer_refer_our_organization = '-'
        score = '-'

        if job.state == WORK_ORDER_STATE.COMPLETED_AND_PAID or job.state == WORK_ORDER_STATE.COMPLETED_BUT_UNPAID:
            was_survey_conducted = 1 if job.was_survey_conducted else 0
            was_job_satisfactory = 1 if job.was_job_satisfactory else 0
            was_job_finished_on_time_and_on_budget = 1 if job.was_job_finished_on_time_and_on_budget else 0
            was_associate_punctual = 1 if job.was_associate_punctual else 0
            was_associate_professional = 1 if job.was_associate_professional else 0
            would_customer_refer_our_organization = 1 if job.would_customer_refer_our_organization else 0
            score = job.score

        # Generate the row.
        rows += ([
            job.id,
            pretty_dt_string(job.assignment_date),
            pretty_dt_string(job.completion_date),
            invoice_service_fee_amount,
            invoice_labour_amount,
            job_type,
            job.get_pretty_status(),
            job.customer.id,
            str(job.customer),
            skill_set_string,
            was_survey_conducted,
            was_job_satisfactory,
            was_job_finished_on_time_and_on_budget,
            was_associate_punctual,
            was_associate_professional,
            would_customer_refer_our_organization,
            score
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="associate_jobs.csv"'
    return response
