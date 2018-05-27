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
from shared_foundation.constants import *
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    Order,
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


def report_05_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    # Generate the CSV header row.
    rows = (["Skill set", "Service Fees Paid", "# of Jobs Completed"],)

    # Fetch all the skill-sets we have in the system.
    skill_sets = SkillSet.objects.all()
    for skill_set in skill_sets.all():

        paid_jobs = Order.objects.filter(
            invoice_service_fee_payment_date__range=(from_dt,to_dt),
            invoice_service_fee_amount__isnull=False,
            skill_sets__id=skill_set.id
        ).order_by('-invoice_service_fee_payment_date')

        from django.db.models import Avg, Count, Min, Sum

        total_count = paid_jobs.count()
        total_paid = paid_jobs.aggregate(total_amount_paid=Sum('invoice_service_fee_amount'))
        total_paid_float = total_paid['total_amount_paid']
        if total_paid_float is None:
            total_paid_float = 0.00

        # Generate the reason.
        rows += ([
            str(skill_set),
            str(total_paid_float),
            str(total_count),
        ],)

    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="service_fees_paid_per_skillset.csv"'
    return response


def report_06_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    cancelled_jobs = Order.objects.filter(
        completion_date__range=(from_dt,to_dt),
        is_cancelled=True
    ).order_by('-completion_date')

    # Generate the CSV header row.
    rows = (["Job ID #", "Date", "Reason", "Associate ID #", "Associate Name"],)

    # Generate hte CSV data.
    for cancelled_job in cancelled_jobs.all():

        # Generate the closing reason.
        closing_reason = cancelled_job.closing_reason_other
        if cancelled_job.closing_reason == 0:
            closing_reason = "-"
        elif cancelled_job.closing_reason == 2:
            closing_reason = _("Client needs more time")
        elif cancelled_job.closing_reason == 3:
            closing_reason = _("Associate needs more time")
        elif cancelled_job.closing_reason == 4:
            closing_reason = _("Weather")

        # Generate the reason.
        rows += ([
            str(cancelled_job.id),
            str(cancelled_job.completion_date),
            str(closing_reason),
            str(cancelled_job.associate.id),
            str(cancelled_job.associate),
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
