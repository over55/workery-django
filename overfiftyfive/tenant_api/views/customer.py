# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.custom_permissions import (
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
    pagination_class = StandardResultsSetPagination
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (
        permissions.IsAuthenticated,
        CanListCreateCustomerPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = Customer.objects.all().order_by('-created')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = CustomerListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (
        permissions.IsAuthenticated,
        CanRetrieveUpdateDestroyCustomerPermission
    )

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

    def put(self, request, pk=None):
        """
        Update
        """
        customer = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(request, customer)  # Validate permissions.
        serializer = CustomerRetrieveUpdateDestroySerializer(customer, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        customer = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(request, customer)  # Validate permissions.
        customer.delete()
        return Response(data=[], status=status.HTTP_200_OK)
