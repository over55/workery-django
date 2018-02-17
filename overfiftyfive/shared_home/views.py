# -*- coding: utf-8 -*-
from django.shortcuts import render


def index_page(request):
    """
    The default entry point into our application.
    """
    return render(request, 'shared_home/index_master_view.html',{
        'current_page': 'home-master',
    })


def http_404_page(request):
    return render(request, 'shared_home/http_404.html',{})


def http_500_page(request):
    return render(request, 'shared_home/http_500.html',{})
