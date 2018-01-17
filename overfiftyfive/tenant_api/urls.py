from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import serializers, viewsets, routers
from rest_framework.urlpatterns import format_suffix_patterns
from tenant_api.views.associate import AssociateListCreateAPIView, AssociateRetrieveUpdateDestroyAPIView
from tenant_api.views.comment import CommentListCreateAPIView, CommentRetrieveUpdateDestroyAPIView
from tenant_api.views.customer import CustomerListCreateAPIView, CustomerRetrieveUpdateDestroyAPIView
from tenant_api.views.order import OrderListCreateAPIView, OrderRetrieveUpdateDestroyAPIView


urlpatterns = [
    url(r'^api/customers$', CustomerListCreateAPIView.as_view(), name='o55_franchise_list_create_api_endpoint'),
]


urlpatterns = format_suffix_patterns(urlpatterns)
