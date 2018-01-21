# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login/")
def master_page(request):
    return render(request, 'tenant_customer/master_view.html',{
        'current_page': 'customer-master',
    })


@login_required(login_url="/login/")
def detail_page(request, pk):
    return render(request, 'tenant_customer/detail_view.html',{
        'current_page': 'customer-master',
    })
