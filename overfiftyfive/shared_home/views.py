# -*- coding: utf-8 -*-
from django.shortcuts import render


def index_page(request):
    """
    The default entry point into our application.
    """
    return render(request, 'shared_home/index_master_view.html',{
        'current_page': 'home-master',
    })
