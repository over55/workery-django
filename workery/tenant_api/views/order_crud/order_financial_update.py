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
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_crud import WorkOrderFinancialUpdateSerializer
from tenant_api.serializers.order_crud.order_retrieve_update_destroy import WorkOrderRetrieveUpdateDestroySerializer
from tenant_foundation.models import WorkOrder


class WorkOrderFinancialUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        order = get_object_or_404(WorkOrder, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        write_serializer = WorkOrderFinancialUpdateSerializer(order, data=request.data, context={'request': request,})
        write_serializer.is_valid(raise_exception=True)
        order = write_serializer.save()
        read_serializer = WorkOrderRetrieveUpdateDestroySerializer(order, many=False, context={'request': request,})
        return Response(read_serializer.data, status=status.HTTP_200_OK)
