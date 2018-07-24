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
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    jobs = WorkOrder.objects.filter(
        ~Q(associate=None) &
        Q(state=WORK_ORDER_STATE.COMPLETED_BUT_UNPAID)
    ).prefetch_related(
        'customer',
        'associate',
        'skill_sets'
    )

    # Generate the CSV header row.
    rows = (["Associate ID #", "Associate Name", "Job Completion Date", "Job ID #", "Client ID #", "Client Name", "Job Type", "Skill Set(s)"],)

    # Generate hte CSV data.
    for job in jobs.all():
        # Get the type of job from a "tuple" object.
        test = dict(JOB_TYPE_OF_CHOICES)
        job_type = test[job.type_of]

        # Attach all the skill sets that are associated with each job.
        skill_set_string = job.get_skill_sets_string()

        rows += ([
            job.associate.id,
            str(job.associate),
            job.completion_date,
            job.id,
            job.customer.id,
            str(job.customer),
            job_type,
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

        paid_jobs = WorkOrder.objects.filter(
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

    cancelled_jobs = WorkOrder.objects.filter(
        Q(completion_date__range=(from_dt,to_dt)) &
        Q(state=WORK_ORDER_STATE.CANCELLED) &
        Q(associate__isnull=False)
    ).order_by('-completion_date')

    # Generate the CSV header row.
    rows = (["Job ID #", "Date", "Reason", "Associate ID #", "Associate Name", "Skill Set(s)"],)

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
            str(cancelled_job.completion_date),
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
    ).order_by(
        'month',
        'day'
    ).prefetch_related(
        'skill_sets',
        'owner'
    )

    filter_type = request.GET.get('filter_type', 'all')
    if filter_type == '1':
        associates = associates.filter(owner__is_active=True)
    elif filter_type == '0':
        associates = associates.filter(owner__is_active=False)

    # Generate the CSV header row.
    rows = (["ID #", "Name", "Birthday", "Skill Set(s)"],)

    # Generate hte CSV data.
    for associate in associates.all():
        skill_set_string = associate.get_skill_sets_string()
        rows += ([
            associate.id,
            str(associate),
            "-" if associate.birthdate is None else associate.birthdate,
            skill_set_string
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="associate_birthdays.csv"'
    return response


def report_10_streaming_csv_view(request):
    associate_id = request.GET.get('associate_id', None)

    associate = Associate.objects.filter(id=associate_id).first()

    # Generate the CSV header row.
    rows = (["Skill Set"],)

    # Generate hte CSV data.
    if associate:
        if associate.skill_sets.count() > 0:
            for skill_set in associate.skill_sets.all():
                rows += ([
                    str(skill_set)
                ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="associate_skill_sets.csv"'
    return response


def report_12_streaming_csv_view(request):
    # DEVELOPERS NOTE:
    # - We will sort by the month and day of the associate's birthdate.
    customers = Customer.objects.all().order_by('last_name', 'given_name', )

    # Generate the CSV header row.
    rows = ([
        "ID #",
        "Name",
        "Type",
        "Ok to email?",
        "Ok to text?",
        "Address",
        "Address (Extra)",
        "City",
        "Province",
        "Country",
        "Postal",
        'Email',
        'Telephone',
        'Telephone Type',
        'Telephone Extension',
        'Other Telephone',
        'Other Telephone Type',
        'Other Telephone Extension',
    ],)

    type_of_choices = dict(CUSTOMER_TYPE_OF_CHOICES)

    tele_type_of_choices = dict(TELEPHONE_CONTACT_POINT_TYPE_OF_CHOICES)

    # Generate hte CSV data.
    for customer in customers.all():

        customer_type_of = type_of_choices[customer.type_of]
        telephone_type_of = tele_type_of_choices[customer.telephone_type_of]
        other_telephone_type_of = tele_type_of_choices[customer.other_telephone_type_of]

        rows += ([
            customer.id,
            customer.last_name+", "+customer.given_name,
            customer_type_of,
            customer.is_ok_to_email,
            customer.is_ok_to_text,
            customer.street_address,
            customer.street_address_extra,
            customer.address_locality,
            customer.address_region,
            customer.address_country,
            customer.postal_code,
            customer.email,
            customer.telephone,
            telephone_type_of,
            customer.telephone_extension,
            customer.other_telephone,
            other_telephone_type_of,
            customer.other_telephone_extension
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    return response


def report_13_streaming_csv_view(request):
    from_dt = request.GET.get('from_dt', None)
    to_dt = request.GET.get('to_dt', None)

    from_dt = parser.parse(from_dt)
    to_dt = parser.parse(to_dt)

    jobs = WorkOrder.objects.filter(
        assignment_date__range=(from_dt,to_dt),
        # associate__isnull=False
    ).order_by('-id')

    # Generate the CSV header row.
    rows = (["Job ID #", "Associate", "Client", 'Skill Sets'],)

    # Generate hte CSV data.
    for job in jobs.all():

        # Get our list of skill sets.
        all_skill_sets = job.skill_sets.all()
        skill_set_text = ""
        for i, skill_set in enumerate(all_skill_sets):
            skill_set_text += skill_set.sub_category
            if i > all_skill_sets.count():
                skill_set_text += " / "

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
    ).order_by('-id')

    # Generate the CSV header row.
    rows = (["Job ID #", "Completion date", "Associate", "Client", "WSIB Date", "Total Labour", "Invoice #", "Skill Sets"],)

    # Generate hte CSV data.
    for job in jobs.all():

        # Get our list of skill sets.
        all_skill_sets = job.skill_sets.all()
        skill_set_text = ""
        for i, skill_set in enumerate(all_skill_sets):
            skill_set_text += skill_set.sub_category
            if i > all_skill_sets.count():
                skill_set_text += " / "

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
