from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from shared_auth.views import email_views
from shared_auth.views import web_views


urlpatterns = (
    # # EMAIL
    # url(r'^activate/(.*)/email/$',
    # email_views.user_activation_email_page,
    # name='o55_register_user_activation_email_master'),

    # WEB
    url(r'^login/$',
    web_views.user_login_master_page,
    name='o55_login_master'),

    url(r'^login/redirector$',
    web_views.user_login_redirector_master_page,
    name='o55_login_redirector'),

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
