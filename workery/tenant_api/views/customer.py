# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.filters.customer import CustomerFilter
from tenant_api.permissions.customer import (
   CanListCreateCustomerPermission,
   CanRetrieveUpdateDestroyCustomerPermission
)
from tenant_api.serializers.customer import (
    CustomerListCreateSerializer,
    CustomerRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import Customer


class CustomerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CustomerListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateCustomerPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    # search_fields = ('@given_name', '@middle_name', '@last_name', '@email', 'telephone',)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = Customer.objects.all().order_by('last_name')

        # The following code will use the 'django-filter'
        filter = CustomerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = CustomerListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyCustomerPermission
    )

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        customer = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(request, customer)  # Validate permissions.
        serializer = CustomerRetrieveUpdateDestroySerializer(customer, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        customer = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(request, customer)  # Validate permissions.
        serializer = CustomerRetrieveUpdateDestroySerializer(customer, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Delete
        """
        customer = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(request, customer)  # Validate permissions.
        customer.delete()
        return Response(data=[], status=status.HTTP_200_OK)


class CustomerCreateValidationAPIView(generics.CreateAPIView):
    """
    API endpoint strictly used for POST creation validations of the customer
    model before an actual POST create API call is made.
    """
    serializer_class = CustomerListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateCustomerPermission
    )

    def post(self, request, format=None):
        """
        Create
        """
        serializer = CustomerListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
