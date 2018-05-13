from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView
from tenant_help import views

urlpatterns = (
    path('help/', views.HelpCategoryListView.as_view(), name='workery_tenant_help_category_list'),

    path('help/category/<int:pk>/', views.HelpCategoryRetrieveView.as_view(), name='workery_tenant_help_category_retrieve'),

    path('help/item/<int:pk>/', views.HelpItemRetrieveView.as_view(), name='workery_tenant_help_item_retrieve'),
)
