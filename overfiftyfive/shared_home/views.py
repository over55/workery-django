# -*- coding: utf-8 -*-
from django.shortcuts import render


def index_page(request):
    """
    The default entry point into our application.
    """
    return render(request, 'shared_home/index_master_view.html',{
        'current_page': 'home-master',
    })


def page_not_found(request, exception, template_name='shared_home/http_404.html'):
    response = render(request, 'shared_home/http_404.html',{})
    response.status_code = 404
    return response


def server_error(request, template_name='shared_home/http_500.html'):
    response = render(request, 'shared_home/http_500.html',{})
    response.status_code = 500
    return response
