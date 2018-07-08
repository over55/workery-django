# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
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
from tenant_api.serializers.ongoing_order import OngoingWorkOrderRetrieveUpdateDestroySerializer
from tenant_foundation.models import OngoingWorkOrder


class OngoingWorkOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OngoingWorkOrderRetrieveUpdateDestroySerializer
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
        order = get_object_or_404(OngoingWorkOrder, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = OngoingWorkOrderRetrieveUpdateDestroySerializer(order, many=False)
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
        order = get_object_or_404(OngoingWorkOrder, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = OngoingWorkOrderRetrieveUpdateDestroySerializer(order, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        order = get_object_or_404(OngoingWorkOrder, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        order.delete()
        return Response(data=[], status=status.HTTP_200_OK)
