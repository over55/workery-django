# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
# from django_filters import rest_framework as filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.order import WorkOrderFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_crud.order_list_create import WorkOrderListCreateSerializer
from tenant_api.serializers.order_crud.order_retrieve_update_destroy import WorkOrderRetrieveUpdateDestroySerializer
from tenant_foundation.models import WorkOrder


class WorkOrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkOrderListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        # CanListCreateWorkOrderPermission # No need for this permission handling.
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch queries based by user account.
        queryset = WorkOrder.objects.none()
        if self.request.user.is_staff():
            queryset = WorkOrder.objects.all().order_by('-created')
        if self.request.user.is_associate():
            queryset = WorkOrder.objects.filter(associate__owner=self.request.user).order_by('-created')

        # Apply our optimization.
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = WorkOrderFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        write_serializer = WorkOrderListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        write_serializer.is_valid(raise_exception=True)
        order_obj = write_serializer.save()
        read_serializer = WorkOrderRetrieveUpdateDestroySerializer(order_obj, many=False)
        return Response(
            data=read_serializer.data,
            status=status.HTTP_201_CREATED
        )

class WorkOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkOrderRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        order = get_object_or_404(WorkOrder, pk=pk)
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
        client_ip, is_routable = get_client_ip(self.request)
        order = get_object_or_404(WorkOrder, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = WorkOrderRetrieveUpdateDestroySerializer(order, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant,
            'state': request.data.get("state", None)
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        order = get_object_or_404(WorkOrder, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        order.delete()
        return Response(data=[], status=status.HTTP_200_OK)
