# -*- coding: utf-8 -*-
from rest_framework.authtoken.models import Token
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from shared_foundation.models import SharedFranchise
from shared_foundation.models import SharedUser
from shared_foundation import utils
from shared_foundation.decorators import public_only_or_redirect


@public_only_or_redirect
def user_login_master_page(request):
    return render(request, 'shared_auth/login_user/master_view.html',{})


@public_only_or_redirect
def user_login_redirector_master_page(request):
    if request.user.is_authenticated:

        # CASE 1 OF 2:
        # First check to see if user belongs to an organization to redirect to.
        franchise = request.user.franchise
        if franchise:
            return HttpResponseRedirect(franchise.reverse('o55_tenant_dashboard_master'))

        # CASE 2 OF 2:
        # Check to see if the authenticated user is a `root` user.
        #TODO: IMPLEMENT.

    # If any errors occure in the redirector then simply redirect to the
    # homepage.
    return HttpResponseRedirect(reverse('o55_index_master', args=[]))


@public_only_or_redirect
def send_reset_password_email_master_page(request):
    return render(request, 'shared_auth/send_reset_password_email/master_view.html',{
        'has_pr_code_expired': request.GET.get('has_pr_code_expired', False),
        'has_wrong_pr_access_code': request.GET.get('has_wrong_pr_access_code', False)
    })


@public_only_or_redirect
def send_reset_password_email_submitted_page(request):
    return render(request, 'shared_auth/send_reset_password_email/detail_view.html',{})


@public_only_or_redirect
def rest_password_master_page(request, pr_access_code):
    try:
        me = SharedUser.objects.get(pr_access_code=pr_access_code)
        if me.has_pr_code_expired():
            return HttpResponseRedirect(reverse('o55_send_reset_password_email_master', args=[])+"?has_pr_code_expired=True")
    except SharedUser.DoesNotExist:
        #TODO: In the future, write code for tracking how many attempts are made
        #      and if too many then block the user. For now just keep this in mind.

        # Error message indicates wrong password was entered.
        return HttpResponseRedirect(reverse('o55_send_reset_password_email_master', args=[])+"?has_wrong_pr_access_code=True")

    return render(request, 'shared_auth/reset_password/master_view.html',{
        'pr_access_code': pr_access_code
    })


@public_only_or_redirect
def rest_password_detail_page(request, pr_access_code): #TEST
    return render(request, 'shared_auth/reset_password/detail_view.html',{})


@public_only_or_redirect
def user_activation_detail_page(request, pr_access_code=None):
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

    return render(request, 'shared_auth/activate_user/detail_view.html',{})


@public_only_or_redirect
@login_required(login_url="login/")
def user_logout_redirector_master_page(request):
    # Step 1: Delete the "auth_token" so our RESTFul API won't have a key.
    Token.objects.filter(user=request.user).delete()

    # Step 2: RESET ALL THE USER PROFILE INFORMATION TO A SESSION.
    request.session['me_token'] = None
    request.session['me_token_orig_iat'] = None
    request.session['me_schema_name'] = None

    # Step 3: Close the Django session.
    logout(request)

    # Step 4: Redirect to the homepage.
    sign_in_url = settings.O55_APP_HTTP_PROTOCOL + settings.O55_APP_HTTP_DOMAIN + reverse('o55_login_master', args=[])
    return HttpResponseRedirect(sign_in_url)
