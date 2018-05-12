# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tenant_foundation.models import (
    Associate,
    AwayLog,
    Customer,
    Order,
    TaskItem
)


@login_required(login_url="login/")
def master_page(request):
    """
    The default entry point into our dashboard.
    """
    return render(request, 'tenant_dashboard/master_view.html',{
        'current_page': 'dashboard', # Required
        'associates_count': Associate.objects.filter(
            owner__is_active=True
        ).count(),
        'customers_count': Customer.objects.all().count(),
        'jobs_count': Order.objects.filter(
            is_cancelled=False,
            completion_date__isnull=True,
            payment_date__isnull=True
        ).count(),
        'tasks_count': TaskItem.objects.filter(
            is_closed=False
        ).count(),
        'awaylogs': AwayLog.objects.filter(was_deleted=False),
    })
