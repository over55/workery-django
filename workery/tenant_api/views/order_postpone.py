# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from starterkit.drf.permissions import IsAuthenticatedAndIsActivePermission
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_postpone import (
    WorkOrderPostponeCreateSerializer,
)
from tenant_foundation.models import ActivitySheetItem


class WorkOrderPostponeCreateAPIView(generics.CreateAPIView):
    serializer_class = WorkOrderPostponeCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderPermission
    )

    def post(self, request, format=None):
        """
        Create
        """
        serializer = WorkOrderPostponeCreateSerializer(data=request.data, context={
            'user': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
