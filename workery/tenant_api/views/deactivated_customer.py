# -*- coding: utf-8 -*-
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.deactivated_customer import DeactivatedCustomerFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.customer import CanListCreateCustomerPermission
from tenant_api.serializers.deactivated_customer import DeactivatedCustomerListSerializer
from tenant_foundation.models import Customer


class DeactivatedCustomerListAPIView(generics.ListAPIView):
    serializer_class = DeactivatedCustomerListSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateCustomerPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all deactivated customers.
        queryset = Customer.objects.filter(
            state=Customer.CUSTOMER_STATE.INACTIVE
        ).order_by(
            '-id'
        ).prefetch_related(
            'owner'
        )

        # The following code will use the 'django-filter'
        filter = DeactivatedCustomerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset
