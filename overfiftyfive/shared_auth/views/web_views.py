# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from shared_foundation.models import SharedFranchise
from shared_foundation.models import SharedMe
from shared_foundation import utils


def user_login_master_page(request):
    return render(request, 'shared_auth/login_user/master_view.html',{})


def user_login_redirector_master_page(request):
    if request.user.is_authenticated:
        franchise = SharedFranchise.objects.get_by_email_or_none(request.user.email)
        if franchise:
            print("-------------------------------")
            print("TODO: PLEASE IMPLEMENT THIS!!!!")
            print("-------------------------------")
            return HttpResponseRedirect(franchise.reverse('o55_index_master', []))

    # If any errors occure in the redirector then simply redirect to the
    # homepage.
    return HttpResponseRedirect(reverse('o55_index_master', args=[]))


def send_reset_password_email_master_page(request):
    return render(request, 'shared_auth/send_reset_password_email/master_view.html',{
        'has_pr_code_expired': request.GET.get('has_pr_code_expired', False),
        'has_wrong_pr_access_code': request.GET.get('has_wrong_pr_access_code', False)
    })


def send_reset_password_email_submitted_page(request):
    return render(request, 'shared_auth/send_reset_password_email/detail_view.html',{})


def rest_password_master_page(request, pr_access_code):
    try:
        me = SharedMe.objects.get(pr_access_code=pr_access_code)
        if me.has_pr_code_expired():
            return HttpResponseRedirect(reverse('o55_send_reset_password_email_master', args=[])+"?has_pr_code_expired=True")
    except SharedMe.DoesNotExist:
        #TODO: In the future, write code for tracking how many attempts are made
        #      and if too many then block the user. For now just keep this in mind.

        # Error message indicates wrong password was entered.
        return HttpResponseRedirect(reverse('o55_send_reset_password_email_master', args=[])+"?has_wrong_pr_access_code=True")

    return render(request, 'shared_auth/reset_password/master_view.html',{
        'pr_access_code': pr_access_code
    })


def rest_password_detail_page(request, pr_access_code): #TEST
    return render(request, 'shared_auth/reset_password/detail_view.html',{})
