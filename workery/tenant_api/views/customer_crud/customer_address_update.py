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
from tenant_api.serializers.customer_crud import CustomerRetrieveUpdateDestroySerializer, CustomerAddressUpdateSerializer
from tenant_foundation.models import Customer


class CustomerAddressUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomerRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyCustomerPermission
    )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        customer = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(request, customer)  # Validate permissions.
        write_serializer = CustomerAddressUpdateSerializer(customer, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        write_serializer.is_valid(raise_exception=True)
        customer = write_serializer.save()
        read_serializer = CustomerRetrieveUpdateDestroySerializer(customer, many=False, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)
