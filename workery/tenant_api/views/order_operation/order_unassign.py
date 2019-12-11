# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.db import transaction
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
from tenant_api.serializers.order_operation.order_unassign import WorkOrderUnassignCreateSerializer
from tenant_foundation.models import ActivitySheetItem


class WorkOrderUnassignOperationCreateAPIView(generics.CreateAPIView):
    serializer_class = WorkOrderUnassignCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = WorkOrderUnassignCreateSerializer(data=request.data, context={
            'user': request.user,
            'from': client_ip,
            'from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
