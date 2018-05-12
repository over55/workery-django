# -*- coding: utf-8 -*-
from functools import wraps
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

# def tenant_required(view_func):
#     """Decorator ensures an subdomain is associated with the view request."""
#     def wrapper(request, *args, **kwargs):
#         if request.tenant.schema_name != "public" and request.tenant.schema_name != "test":
#             return view_func(request, *args, **kwargs)
#         else:
#             return HttpResponseForbidden(
#                 _("Missing tenant.")
#             )
#     return wrapper


def public_only_or_redirect(view_func):
    """
    Decorator ensures a request with a subdomain will cause a redirect to the
    non-subdomain URL version of this request or do nothing with the request.
    """
    def wrapper(request, *args, **kwargs):
        # CASE 1 OF 2:
        # If we are the public tenant then render the page.
        if request.tenant.is_public():
            return view_func(request, *args, **kwargs)

        # CASE 2 OF 2:
        # If we are a tenant then we need to redirect to the public base page.
        url = settings.O55_APP_HTTP_PROTOCOL
        url += settings.O55_APP_HTTP_DOMAIN
        url = url + request.path
        return HttpResponseRedirect(url)
    return wrapper
