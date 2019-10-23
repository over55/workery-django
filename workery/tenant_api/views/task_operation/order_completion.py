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
from tenant_api.permissions.task_item import (
   CanListCreateTaskItemPermission,
   CanRetrieveUpdateDestroyTaskItemPermission
)
from tenant_api.serializers.task_operation.order_completion import OrderCompletionTaskOperationSerializer
from tenant_foundation.models import ActivitySheetItem


#TODO: INTEGRATE


class OrderCompletionTaskOperationAPIView(generics.CreateAPIView):
    serializer_class = OrderCompletionTaskOperationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateTaskItemPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = OrderCompletionTaskOperationSerializer(data=request.data, context={
            'user': request.user,
            'from': client_ip,
            'from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
