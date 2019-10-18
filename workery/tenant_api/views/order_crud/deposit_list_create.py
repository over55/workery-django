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
from shared_foundation import utils
from tenant_api.filters.order_deposit import WorkOrderDepositFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_crud import WorkOrderDepositListCreateSerializer
from tenant_api.serializers.order_crud import WorkOrderDepositRetrieveDeleteSerializer
from tenant_foundation.models import WorkOrderDeposit


class WorkOrderDepositListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkOrderDepositListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Extract the order id.
        order_id = utils.int_or_none(self.kwargs.get("pk"))

        # Fetch all the queries.
        queryset = WorkOrderDeposit.objects.filter(order=order_id).order_by('-created_at')
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = WorkOrderDepositFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, pk=None):
        """
        Create
        """
        order_id = utils.int_or_none(pk)
        client_ip, is_routable = get_client_ip(self.request)
        write_serializer = WorkOrderDepositListCreateSerializer(data=request.data, context={
            'order_id': order_id,
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        write_serializer.is_valid(raise_exception=True)
        order_obj = write_serializer.save()
        read_serializer = WorkOrderDepositRetrieveDeleteSerializer(order_obj, many=False)
        return Response(
            data=read_serializer.data,
            status=status.HTTP_201_CREATED
        )

# class WorkOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = WorkOrderRetrieveUpdateDestroySerializer
#     pagination_class = TinyResultsSetPagination
#     permission_classes = (
#         permissions.IsAuthenticated,
#         IsAuthenticatedAndIsActivePermission,
#         CanRetrieveUpdateDestroyWorkOrderPermission
#     )
#
#     def get(self, request, pk=None):
#         """
#         Retrieve
#         """
#         order = get_object_or_404(WorkOrder, pk=pk)
#         self.check_object_permissions(request, order)  # Validate permissions.
#         serializer = WorkOrderRetrieveUpdateDestroySerializer(order, many=False)
#         # queryset = serializer.setup_eager_loading(self, queryset)
#         return Response(
#             data=serializer.data,
#             status=status.HTTP_200_OK
#         )
#
#     def put(self, request, pk=None):
#         """
#         Update
#         """
#         client_ip, is_routable = get_client_ip(self.request)
#         order = get_object_or_404(WorkOrder, pk=pk)
#         self.check_object_permissions(request, order)  # Validate permissions.
#         serializer = WorkOrderRetrieveUpdateDestroySerializer(order, data=request.data, context={
#             'last_modified_by': request.user,
#             'last_modified_from': client_ip,
#             'last_modified_from_is_public': is_routable,
#             'franchise': request.tenant,
#             'state': request.data.get("state", None)
#         })
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def delete(self, request, pk=None):
#         """
#         Delete
#         """
#         order = get_object_or_404(WorkOrder, pk=pk)
#         self.check_object_permissions(request, order)  # Validate permissions.
#         order.delete()
#         return Response(data=[], status=status.HTTP_200_OK)
