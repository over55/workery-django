# -*- coding: utf-8 -*-
from functools import wraps
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language


def tenant_required_or_404(view_func):
    """
    Decorator ensures sub-domain is associated with the view request maps to
    an existing (non-public) tenant or else return a 404 error.
    """
    def wrapper(request, *args, **kwargs):
        if not request.tenant.is_public():
            return view_func(request, *args, **kwargs)
        else:
            raise Http404()
    return wrapper
