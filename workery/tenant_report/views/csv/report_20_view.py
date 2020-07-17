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


def report_20_streaming_csv_view(request):
    # Get our user parameters.
    naive_from_dt = request.GET.get('from_dt', None)
    naive_to_dt = request.GET.get('to_dt', None)

    # Convert our datatime `string` into a `datatime` object.
    naive_from_dt = parser.parse(naive_from_dt)
    naive_to_dt = parser.parse(naive_to_dt)

    # Convert our aware datetimes to the specific timezone of the tenant.
    today = timezone.now()
    tenant_today = request.tenant.to_tenant_dt(today)
    tenant_from_dt = request.tenant.localize_tenant_dt(naive_from_dt)
    tenant_from_d = tenant_from_dt.date()
    tenant_to_dt = request.tenant.localize_tenant_dt(naive_to_dt)
    tenant_to_d = tenant_to_dt.date()

    # Run our filter lookup.
    jobs = WorkOrder.objects.filter(
        invoice_service_fee_payment_date__range=(tenant_from_dt,tenant_to_dt),
        # associate__isnull=False
    ).order_by(
       '-invoice_service_fee_payment_date'
    ).prefetch_related(
        'customer',
        'associate',
        'skill_sets',
    )

    # Generate our new header.
    rows = (["Payments Report","","",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"",],)
    rows += (["From Payment Date:", pretty_dt_string(tenant_from_d),"",],)
    rows += (["To Payment Date:", pretty_dt_string(tenant_to_d),"",],)
    rows += (["", "","",],)
    rows += (["", "","",],)

    # Generate the CSV header row.
    rows += ([
        "Associate No.",
        "Associate",
        "Assignment Date",
        "Associate DOB",
        "Associate Age",
        "Job No.",
        "Client No.",
        "Client",
        "Client Birthdate",
        "Client Age",
        "Score",
        "Labour Actual",
        "Material Actual",
        "Other Actual",
        "Sub-Total",
        "Tax",
        "Total",
        "Deposit",
        "Amount Due",
        "Service Fee Due",
        "Service Fee Paid",
        "Service Fee",
    ],)

    # Generate hte CSV data.
    for job in jobs.all():

        # Get our DOB and age.
        associate_id = None
        associate_dob = None
        associate_age = None
        if job.associate:
            associate_id = job.associate.id
            associate_dob = pretty_dt_string(job.associate.birthdate) if job.associate.birthdate is not None else ""
            associate_age = job.associate.get_current_age()
        customer_dob = pretty_dt_string(job.customer.birthdate) if job.customer.birthdate is not None else ""

        invoice_labour_amount = str(job.invoice_labour_amount)
        invoice_labour_amount = invoice_labour_amount.replace('C', '')

        invoice_material_amount = str(job.invoice_material_amount)
        invoice_material_amount = invoice_material_amount.replace('C', '')

        invoice_other_costs_amount = str(job.invoice_other_costs_amount)
        invoice_other_costs_amount = invoice_other_costs_amount.replace('C', '')

        invoice_sub_total_amount = str(job.invoice_sub_total_amount)
        invoice_sub_total_amount = invoice_sub_total_amount.replace('C', '')

        invoice_tax_amount = str(job.invoice_tax_amount)
        invoice_tax_amount = invoice_tax_amount.replace('C', '')

        invoice_total_amount = str(job.invoice_total_amount)
        invoice_total_amount = invoice_total_amount.replace('C', '')

        invoice_deposit_amount = str(job.invoice_deposit_amount)
        invoice_deposit_amount = invoice_deposit_amount.replace('C', '')

        invoice_amount_due = str(job.invoice_amount_due)
        invoice_amount_due = invoice_amount_due.replace('C', '')


        invoice_service_fee_amount = str(job.invoice_service_fee_amount)
        invoice_service_fee_amount = invoice_service_fee_amount.replace('C', '')

        invoice_actual_service_fee_amount_paid = str(job.invoice_actual_service_fee_amount_paid)
        invoice_actual_service_fee_amount_paid = invoice_actual_service_fee_amount_paid.replace('C', '')

        # Generate the reason.
        rows += ([
            str(associate_id),
            str(job.associate),
            pretty_dt_string(job.assignment_date),
            str(associate_dob),
            associate_age,
            str(job.id),
            str(job.customer.id),
            str(job.customer),
            str(customer_dob),
            job.customer.get_current_age(),
            str(job.score),
            str(invoice_labour_amount),
            str(invoice_material_amount),
            str(invoice_other_costs_amount),
            str(invoice_sub_total_amount),
            str(invoice_tax_amount),
            str(invoice_total_amount),
            str(invoice_deposit_amount),
            str(invoice_amount_due),
            str(invoice_service_fee_amount),
            str(invoice_actual_service_fee_amount_paid),
            str(job.invoice_service_fee.title)
        ],)

        # Labour Actual
        # Material Actual
        # Service fee (calculated at the rate) eg 15%
        # SERVICE FEE PAID
        # Service fee owing (if any)


    # Create the virtual CSV file and stream all the data in real time to the
    # client.
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'
    return response
