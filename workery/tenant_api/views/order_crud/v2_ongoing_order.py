# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.ongoing_order import OngoingWorkOrderFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_crud.ongoing_order_list_create import OngoingWorkOrderCreateSerializer
from tenant_api.serializers.order_crud import (
    OngoingWorkOrderRetrieveSerializer,
    OngoingWorkOrderUpdateSerializer
)
from tenant_foundation.models import OngoingWorkOrder


class OngoingWorkOrderListCreateV2APIView(generics.ListCreateAPIView):
    serializer_class = OngoingWorkOrderCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = OngoingWorkOrder.objects.all().order_by('-created')
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)

        # The following code will use the 'django-filter'
        filter = OngoingWorkOrderFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = OngoingWorkOrderCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OngoingWorkOrderRetrieveUpdateDestroyV2APIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        order = get_object_or_404(OngoingWorkOrder, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = OngoingWorkOrderRetrieveSerializer(order, many=False)
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
        ongoing_order = get_object_or_404(OngoingWorkOrder, pk=pk)
        self.check_object_permissions(request, ongoing_order)  # Validate permissions.
        write_serializer = OngoingWorkOrderUpdateSerializer(ongoing_order, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        write_serializer.is_valid(raise_exception=True)
        ongoing_order = write_serializer.save()
        read_serializer = OngoingWorkOrderRetrieveSerializer(ongoing_order, many=False, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        ongoing_order = get_object_or_404(OngoingWorkOrder, pk=pk)
        self.check_object_permissions(request, ongoing_order)  # Validate permissions.
        ongoing_order.delete()
        return Response(data=[], status=status.HTTP_200_OK)
