# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tenant_foundation.decorators import tenant_required_or_404
from tenant_foundation.models.associate import Associate
from tenant_foundation.models.customer import Customer
from tenant_foundation.models.order import Order


@login_required(login_url="login/")
@tenant_required_or_404
def master_page(request):
    """
    The default entry point into our dashboard.
    """
    return render(request, 'tenant_dashboard/master_view.html',{
        'current_page': 'dashboard', # Required
        'associates_count': Associate.objects.all().count(),
        'customers_count': Customer.objects.all().count(),
        'jobs_count': Order.objects.all().count()
    })
