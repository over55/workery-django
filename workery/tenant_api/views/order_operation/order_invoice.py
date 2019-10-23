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
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_operation.order_invoice import WorkOrderInvoiceCreateOrUpdateOperationSerializer
from tenant_api.serializers.order_crud.order_retrieve_update_destroy import WorkOrderRetrieveUpdateDestroySerializer
from tenant_foundation.models import WorkOrder


class WorkOrderInvoiceCreateOrUpdateOperationAPIView(generics.CreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        # CanListCreateWorkOrderPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        if not self.request.user.is_staff() and not self.request.user.is_associate():
            return Response(
                data={'detail':'You do not have permission.'},
                status=status.HTTP_403_FORBIDDEN
            )

        client_ip, is_routable = get_client_ip(self.request)
        serializer = WorkOrderInvoiceCreateOrUpdateOperationSerializer(data=request.data, context={
            'user': request.user,
            'from': client_ip,
            'from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        read_serializer = WorkOrderRetrieveUpdateDestroySerializer(order, many=False)
        return Response(
            data=read_serializer.data,
            status=status.HTTP_201_CREATED
        )
