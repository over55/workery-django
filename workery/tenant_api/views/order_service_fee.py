# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.order_service_fee import WorkOrderServiceFeeFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.order_service_fee import (
   CanListCreateWorkOrderServiceFeePermission,
   CanRetrieveUpdateDestroyWorkOrderServiceFeePermission
)
from tenant_api.serializers.order_service_fee import (
    WorkOrderServiceFeeListCreateSerializer,
    WorkOrderServiceFeeRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import WorkOrderServiceFee


class WorkOrderServiceFeeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkOrderServiceFeeListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderServiceFeePermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = WorkOrderServiceFee.objects.all().order_by('title')

        # The following code will use the 'django-filter'
        filter = WorkOrderServiceFeeFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = WorkOrderServiceFeeListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkOrderServiceFeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkOrderServiceFeeRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderServiceFeePermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        order_service_fee = get_object_or_404(WorkOrderServiceFee, pk=pk)
        self.check_object_permissions(request, order_service_fee)  # Validate permissions.
        serializer = WorkOrderServiceFeeRetrieveUpdateDestroySerializer(order_service_fee, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        order_service_fee = get_object_or_404(WorkOrderServiceFee, pk=pk)
        self.check_object_permissions(request, order_service_fee)  # Validate permissions.
        serializer = WorkOrderServiceFeeRetrieveUpdateDestroySerializer(order_service_fee, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        client_ip, is_routable = get_client_ip(self.request)
        order_service_fee = get_object_or_404(WorkOrderServiceFee, pk=pk)
        self.check_object_permissions(request, order_service_fee)  # Validate permissions.
        order_service_fee.is_archived = True
        order_service_fee.last_modified_by = request.user
        order_service_fee.last_modified_from = client_ip
        order_service_fee.last_modified_from_is_public = is_routable
        order_service_fee.save()
        return Response(data=[], status=status.HTTP_200_OK)
