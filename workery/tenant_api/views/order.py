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
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order import (
    WorkOrderListCreateSerializer,
    WorkOrderRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import WorkOrder


class WorkOrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkOrderListCreateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = WorkOrder.objects.all().order_by('-created')
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = WorkOrderListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkOrderRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = WorkOrderRetrieveUpdateDestroySerializer(order, many=False)
        # queryset = serializer.setup_eager_loading(self, queryset)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = WorkOrderRetrieveUpdateDestroySerializer(order, data=request.data, context={
            'last_modified_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        order.delete()
        return Response(data=[], status=status.HTTP_200_OK)
