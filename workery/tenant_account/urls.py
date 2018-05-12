from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_account import views


urlpatterns = (
    # Update
    path('account/detail/<int:pk>/', views.AccountUpdateView.as_view(), name='o55_tenant_account_update'),
)
