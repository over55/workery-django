# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import condition


def index_page(request):
    """
    The default entry point into our application.
    """
    print("TODO: Implement.")
    return render(request, 'home/master_view.html',{
        'menu': 'index-master',
    })
