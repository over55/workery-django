from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import serializers, viewsets, routers
from rest_framework.urlpatterns import format_suffix_patterns
from shared_api.views.auth_login_view import LoginAPIView
from shared_api.views.auth_logout_view import LogoutAPIView
from shared_api.views.auth_send_reset_password_email_views import SendResetPasswordEmailAPIView
from shared_api.views.auth_reset_password_views import ResetPasswordAPIView
from shared_api.views.franchise_views import (
    SharedFranchiseListCreateAPIView,
    SharedFranchiseRetrieveDeleteDestroyAPIView,
    SharedFranchiseCreateValidationAPIView
)
from shared_api.views.country_and_province_views import get_countries
from shared_api.views.country_and_province_views import get_provinces

urlpatterns = [
    #----------------------#
    # Shared API-endpoints #
    #----------------------#

    # Authentication.
    url(r'^api/login$', LoginAPIView.as_view(), name='workery_login_api_endpoint'),
    url(r'^api/logout$', LogoutAPIView.as_view(), name='workery_logout_api_endpoint'),
    url(r'^api/reset-password$', ResetPasswordAPIView.as_view(), name='workery_reset_password_api_endpoint'),
    url(r'^api/send-reset-password-email$', SendResetPasswordEmailAPIView.as_view(), name='workery_send_reset_password_email_api_endpoint'),

    # Application.
    url(r'^api/franchises$', SharedFranchiseListCreateAPIView.as_view(), name='workery_franchise_list_create_api_endpoint'),
    url(r'^api/franchise/(?P<pk>[^/.]+)/$', SharedFranchiseRetrieveDeleteDestroyAPIView.as_view(), name='workery_franchise_retrieve_update_delete_api_endpoint'),
    url(r'^api/franchises/validate$', SharedFranchiseCreateValidationAPIView.as_view(), name='workery_franchise_pre_create_validation_api_endpoint'),

    # JWT
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),

    # Country / Provinces
    url(r'^api/get_countries$', get_countries, name='workery_get_countries_api_endpoint'),
    url(r'^api/get_provinces$', get_provinces, name='workery_get_provinces_api_endpoint'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
