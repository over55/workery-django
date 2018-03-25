# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import condition
from shared_foundation import constants
from shared_foundation.models import SharedUser
from shared_foundation.utils import reverse_with_full_domain


def reset_password_email_page(request, pr_access_code=None):
    # Find the user or error.
    try:
        me = SharedUser.objects.get(pr_access_code=pr_access_code)
        if not me.has_pr_code_expired():
            # Indicate that the account is active.
            me.was_activated = True
            me.save()
        else:
            # Erro message indicating code expired.
            raise PermissionDenied(_('Access code expired.'))
    except SharedUser.DoesNotExist:
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

    # DEVELOPERS NOTE:
    # - When copying the "Sunday" open source email theme into our code, we will
    #   need to use a formatter to inline the CSS.
    # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'shared_auth/email/reset_password_email.html', param)


def user_activation_email_page(request, pr_access_code=None):
    # Find the user or error.
    try:
        me = SharedUser.objects.get(pr_access_code=pr_access_code)
        if not me.has_pr_code_expired():
            # Indicate that the account is active.
            me.was_activated = True
            me.save()
        else:
            # Erro message indicating code expired.
            raise PermissionDenied(_('Access code expired.'))
    except SharedUser.DoesNotExist:
        raise PermissionDenied(_('Wrong access code.'))

    # Generate the data.
    url = reverse_with_full_domain(
        reverse_url_id='o55_user_activation_detail',
        resolve_url_args=[pr_access_code]
    )
    web_view_url = reverse_with_full_domain(
        reverse_url_id='o55_activate_email',
        resolve_url_args=[pr_access_code]
    )
    param = {
        'constants': constants,
        'url': url,
        'web_view_url': web_view_url,
        'me': me
    }

    # DEVELOPERS NOTE:
    # - When copying the "Sunday" open source email theme into our code, we will
    #   need to use a formatter to inline the CSS.
    # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'shared_auth/email/user_activation_email_view.html', param)
