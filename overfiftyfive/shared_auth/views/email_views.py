# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.views.decorators.http import condition
from shared_foundation.models import SharedMe
from shared_foundation.utils import reverse_with_full_domain


def reset_password_email_page(request, pr_access_code=None):
    # Generate the data.
    url = reverse_with_full_domain(
        reverse_url_id='o55_reset_password_master',
        resolve_url_args=[pr_access_code]
    )
    web_view_extra_url = reverse_with_full_domain(
        reverse_url_id='o55_reset_password_email',
        resolve_url_args=[pr_access_code]
    )
    param = {
        'url': url,
        'web_view_url': web_view_extra_url,
    }
    return render(request, 'email/activate_email_view.html', param)
