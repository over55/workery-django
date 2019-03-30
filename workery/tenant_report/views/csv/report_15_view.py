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


def report_15_streaming_csv_view(request):
    # DEVELOPERS NOTE:
    # - We will sort by the month and day of the associate's birthdate.
    associates = Associate.objects.filter(
        owner__is_active=True
    ).prefetch_related(
        'owner'
    )

    filter_date_type = request.GET.get('filter_date_type', '0')
    filter_days = int(request.GET.get('filter_days', '60'))
    filter_desc = "All relevant date fields by "+str(filter_days)+' days'

    # Convert our aware datetimes to the specific timezone of the tenant.
    tenant_today = request.tenant.get_todays_date_plus_days(0)
    date_plus_filter_days = request.tenant.get_todays_date_plus_days(filter_days)

    # Apply our filtering.
    if filter_date_type == '1':
        filter_desc = "Commercial insurance will expiry within the next "+str(filter_days)+' days'
        associates = associates.filter(commercial_insurance_expiry_date__lte=date_plus_filter_days)
        associates = associates.order_by('commercial_insurance_expiry_date')
    elif filter_date_type == '2':
        filter_desc = "Police check will expiry within the next "+str(filter_days)+' days.'
        associates = associates.filter(police_check__lte=date_plus_filter_days)
        associates = associates.order_by('police_check')
    else:
        associates = associates.filter(
            Q(commercial_insurance_expiry_date__lte=date_plus_filter_days)|
            Q(police_check__lte=date_plus_filter_days)
        )
        associates = associates.order_by('police_check')

    # Generate our new header.
    rows = (["Associate Upcoming expiry dates","","","",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"","",],)
    rows += (["Filter:", filter_desc,"","",],)
    rows += (["", "","","",],)
    rows += (["", "","","",],)

    # Generate the CSV header row.
    rows += (["Associate No.", "Name", "Commercial Insurance", "Police Check"],)

    # Generate hte CSV data.
    for associate in associates.all():
        skill_set_string = associate.get_skill_sets_string()
        rows += ([
            associate.id,
            str(associate),
            "-" if associate.commercial_insurance_expiry_date is None else pretty_dt_string(associate.commercial_insurance_expiry_date),
            "-" if associate.police_check is None else pretty_dt_string(associate.police_check),
        ],)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="associate_expiry_dates.csv"'
    return response
