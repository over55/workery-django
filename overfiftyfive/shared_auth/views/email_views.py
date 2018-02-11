# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import condition
from shared_foundation import constants
from shared_foundation.models import SharedMe
from shared_foundation.utils import reverse_with_full_domain


def reset_password_email_page(request, pr_access_code=None):
    # Find the user or error.
    try:
        me = SharedMe.objects.get(pr_access_code=pr_access_code)
        if not me.has_pr_code_expired():
            # Indicate that the account is active.
            me.was_activated = True
            me.save()
        else:
            # Erro message indicating code expired.
            raise PermissionDenied(_('Access code expired.'))
    except SharedMe.DoesNotExist:
        raise PermissionDenied(_('Wrong access code.'))

    # Generate the data.
    url = reverse_with_full_domain(
        reverse_url_id='o55_reset_password_master',
        resolve_url_args=[pr_access_code]
    )
    web_view_url = reverse_with_full_domain(
        reverse_url_id='o55_reset_password_email',
        resolve_url_args=[pr_access_code]
    )
    param = {
        'constants': constants,
        'url': url,
        'web_view_url': web_view_url,
        'me': me
    }
    return render(request, 'shared_auth/email/reset_password_email.html', param)
