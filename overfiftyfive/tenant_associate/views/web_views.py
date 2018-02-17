# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login/")
def master_page(request):
    return render(request, 'tenant_associate/master_view.html',{
        'current_page': 'associates',
    })


@login_required(login_url="/login/")
def detail_page(request, pk):
    return render(request, 'tenant_associate/detail_view.html',{
        'current_page': 'associates',
    })
