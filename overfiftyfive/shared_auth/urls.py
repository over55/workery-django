from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from shared_auth.views import email_views
from shared_auth.views import web_views


urlpatterns = (
    # # EMAIL
    # Email Views
    # url(r'^activate-email/(.*)/$', email_views.activate_email_page, name='trcag_activate_email'),
    url(r'^reset-password-email/(.*)/$', email_views.reset_password_email_page, name='o55_reset_password_email'),

    # WEB
    url(r'^login/$',
    web_views.user_login_master_page,
    name='o55_login_master'),

    url(r'^login/redirector$',
    web_views.user_login_redirector_master_page,
    name='o55_login_redirector'),

    url(r'^reset/$',
    web_views.send_reset_password_email_master_page,
    name='o55_send_reset_password_email_master'),

    url(r'^reset/submitted$',
    web_views.send_reset_password_email_submitted_page,
    name='o55_send_reset_password_email_submitted'),

    url(r'^reset/(.*)/$',
    web_views.rest_password_master_page,
    name='o55_reset_password_master'),

    # url(r'^register/$',
    # web_views.register_user_master_page,
    # name='o55_register_master'),
    #
    # url(r'^register/done$',
    # web_views.register_user_detail_page,
    # name='o55_register_detail'),
    #
    # url(r'^activate/(.*)/$',
    # web_views.user_activation_detail_page,
    # name='o55_register_user_activation_detail'),
)
