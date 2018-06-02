# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from starterkit.drf.permissions import IsAuthenticatedAndIsActivePermission
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from tenant_api.pagination import StandardResultsSetPagination
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
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderServiceFeePermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = WorkOrderServiceFee.objects.all().order_by('text')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = WorkOrderServiceFeeListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkOrderServiceFeeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkOrderServiceFeeRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderServiceFeePermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        order_service_fee = get_object_or_404(OrderServiceFee, pk=pk)
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
        order_service_fee = get_object_or_404(OrderServiceFee, pk=pk)
        self.check_object_permissions(request, order_service_fee)  # Validate permissions.
        serializer = WorkOrderServiceFeeRetrieveUpdateDestroySerializer(order_service_fee, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        order_service_fee = get_object_or_404(OrderServiceFee, pk=pk)
        self.check_object_permissions(request, order_service_fee)  # Validate permissions.
        order_service_fee.delete()
        return Response(data=[], status=status.HTTP_200_OK)
