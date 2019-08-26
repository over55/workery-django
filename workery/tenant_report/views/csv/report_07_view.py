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


def report_07_streaming_csv_view(request):
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

    filter_desc = "All associates"
    filter_type = request.GET.get('filter_type', 'all')
    if filter_type == '1':
        filter_desc = "Active associates"
        associates = associates.filter(owner__is_active=True)
    elif filter_type == '0':
        filter_desc = "Inactive associates"
        associates = associates.filter(owner__is_active=False)

    # Convert our aware datetimes to the specific timezone of the tenant.
    today = timezone.now()
    tenant_today = request.tenant.to_tenant_dt(today)

    # Generate our new header.
    rows = (["Associate Birthdays","","","",],)
    rows += (["Report Date:", pretty_dt_string(tenant_today),"","",],)
    rows += (["Filter:", filter_desc,"","",],)
    rows += (["", "","","",],)
    rows += (["", "","","",],)

    # Generate the CSV header row.
    rows += (["Associate No.", "Name", "Birthday", "Join Date", "Skill Set(s)"],)

    # Generate hte CSV data.
    for associate in associates.all():
        skill_set_string = associate.get_skill_sets_string()
        rows += ([
            associate.id,
            str(associate),
            "-" if associate.birthdate is None else pretty_dt_string(associate.birthdate),
            "-" if associate.join_date is None else pretty_dt_string(associate.join_date),
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
