# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.cache import cache_page


@cache_page(60 * 15) # 60 seconds per 1 minute x 15 minutes
def index_page(request):
    """
    The default entry point into our application.
    """
    return render(request, 'shared_home/index_master_view.html',{
        'menu_id': 'home-master',
    })


def page_not_found(request, exception, template_name='shared_home/http_404.html'):
    response = render(request, 'shared_home/http_404.html',{})
    response.status_code = 404
    return response


def server_error(request, template_name='shared_home/http_500.html'):
    response = render(request, 'shared_home/http_500.html',{})
    response.status_code = 500
    return response


def bad_request(request, exception, template_name='shared_home/http_400.html'):
    response = render(request, 'shared_home/http_400.html',{})
    response.status_code = 400
    return response
