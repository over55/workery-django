# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from shared_foundation.models import SharedMe
from shared_foundation import utils


def user_login_master_page(request):
    return render(request, 'shared_auth/login_user/master_view.html',{})


@login_required(login_url='/login/')
def user_login_redirector_master_page(request):
    #TODO: IMPLEMENT/
    return HttpResponseRedirect(reverse('o55_index_master', args=[]))

    # raise PermissionDenied(_('TODO: WRITE SOMETHING.'))


def send_reset_password_email_master_page(request):
    return render(request, 'shared_auth/send_reset_password_email/master_view.html',{})


def send_reset_password_email_submitted_page(request):
    return render(request, 'shared_auth/send_reset_password_email/detail_view.html',{})


def rest_password_master_page(request, pr_access_code):
    try:
        me = SharedMe.objects.get(pr_access_code=pr_access_code)
        if me.has_pr_code_expired():
            # Error message indicating code expired.
            raise PermissionDenied(_('Password Reset Access code has expired. Please generate another one...'))
    except SharedMe.DoesNotExist:
        #TODO: In the future, write code for tracking how many attempts are made
        #      and if too many then block the user. For now just keep this in mind.

        # Error message indicates wrong password was entered.
        raise PermissionDenied(_('Wrong access code.'))

    return render(request, 'shared_auth/reset_password/master_view.html',{
        'pr_access_code': pr_access_code
    })


def rest_password_detail_page(request, pr_access_code):
    return render(request, 'shared_auth/reset_password/detail_view.html',{})
