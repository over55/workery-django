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


def report_01_streaming_csv_view(request):
    # Get our user parameters.
    naive_from_dt = request.GET.get('from_dt', None)
    naive_to_dt = request.GET.get('to_dt', None)
    state = request.GET.get('state', WORK_ORDER_STATE.COMPLETED_BUT_UNPAID)

    # Convert our datatime `string` into a `datatime` object.
    naive_from_dt = parser.parse(naive_from_dt)
    naive_to_dt = parser.parse(naive_to_dt)

    # Convert our naive datetimes to the aware datetimes based on the specific
    # timezone of the tenant.
    today = timezone.now()
    today = request.tenant.to_tenant_dt(today)
    from_dt = request.tenant.localize_tenant_dt(naive_from_dt)
    from_d = from_dt.date()
    to_dt = request.tenant.localize_tenant_dt(naive_to_dt)
    to_d = to_dt.date()

    # Run our filter lookup.
    jobs = None
    if state == 'all':
        jobs = WorkOrder.objects.filter(
            ~Q(associate=None) &
            Q(
                Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID) |
                Q(state=WORK_ORDER_STATE.COMPLETED_AND_PAID) |
                Q(state=WORK_ORDER_STATE.IN_PROGRESS)
            ) &
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
            ~Q(associate=None) &
            Q(state=state) &
            Q(assignment_date__range=(from_dt,to_dt))
        ).order_by(
            '-assignment_date'
        ).prefetch_related(
            'customer',
            'associate',
            'skill_sets'
        )

    # Generate our new header.
    rows = (["Service Fee Data Report","","","","","","","","","",""],)
    rows += (["Report Date:", pretty_dt_string(today),"","","","","","","","",""],)
    rows += (["From Assignment Date:", pretty_dt_string(from_d),"","","","","","","","",""],)
    rows += (["To Assignment Date:", pretty_dt_string(to_d),"","","","","","","","",""],)
    rows += (["","","","","","","","","","",""],)
    rows += (["","","","","","","","","","",""],)

    # Generate the CSV header row.
    rows += ([
        "Associate No.",
        "Assignment Date",
        "Associate Name",
        "Associate Gender",
        "Associate DOB",
        "Associate Age",
        "Job Completion Date",
        "Job No.",
        "Service Fee",
        "Actual Service Fee Paid",
        "Job Labour",
        "Job Type",
        "Job Status",
        "Service Fee Date Paid",
        "Client No.",
        "Client Name",
        "Client Gender",
        "Client DOB",
        "Client Age",
        "Skill Set(s)"],)

    # Generate hte CSV data.
    for job in jobs.iterator():
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
        invoice_actual_service_fee_amount_paid = str(job.invoice_actual_service_fee_amount_paid)
        invoice_actual_service_fee_amount_paid = invoice_actual_service_fee_amount_paid.replace('C', '')

        # Format date of birth (dob)
        associate_dob = pretty_dt_string(job.associate.birthdate) if job.associate.birthdate is not None else ""
        customer_dob = pretty_dt_string(job.customer.birthdate) if job.customer.birthdate is not None else ""

        # Format gender.
        associate_gender = str(job.associate.gender) if job.associate.gender is not None else ""
        customer_gender = str(job.customer.gender) if job.customer.gender is not None else ""

        # Generate the row.
        rows += ([
            job.associate.id,
            pretty_dt_string(job.assignment_date),
            str(job.associate),
            associate_gender,
            associate_dob,
            job.associate.get_current_age(),
            pretty_dt_string(job.completion_date),
            job.id,
            invoice_service_fee_amount,
            invoice_actual_service_fee_amount_paid,
            invoice_labour_amount,
            job_type,
            job.get_pretty_status(),
            job.invoice_service_fee_payment_date,
            job.customer.id,
            str(job.customer),
            customer_gender,
            customer_dob,
            job.customer.get_current_age(),
            skill_set_string
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="due_service_fees.csv"'
    return response
