# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login/")
def master_page(request):
    """
    The default entry point into our dashboard.
    """
    return render(request, 'tenant_dashboard/master_view.html',{
        'current_page': 'dashboard-master',
    })
