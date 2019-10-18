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
from tenant_api.serializers.order_crud import WorkOrderDepositRetrieveDeleteSerializer
from tenant_foundation.models import WorkOrderDeposit


class WorkOrderDepositDeleteAPIView(generics.UpdateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    @transaction.atomic
    def delete(self, request, order_pk=None, payment_pk=None):
        """
        Delete
        """
        client_ip, is_routable = get_client_ip(self.request)
        deposit = get_object_or_404(WorkOrderDeposit, pk=payment_pk)
        self.check_object_permissions(request, deposit.order)  # Validate permissions.
        read_serializer = WorkOrderDepositRetrieveDeleteSerializer(deposit, many=False, context={
            'deposit': deposit,
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        read_serializer.delete()
        return Response(
            data=read_serializer.data,
            status=status.HTTP_201_CREATED
        )
