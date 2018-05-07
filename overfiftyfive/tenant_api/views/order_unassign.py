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
   CanListCreateOrderPermission,
   CanRetrieveUpdateDestroyOrderPermission
)
from tenant_api.serializers.order_unassign import OrderUnassignCreateSerializer
from tenant_foundation.models import ActivitySheetItem


class OrderUnassignCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderUnassignCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateOrderPermission
    )

    def post(self, request, format=None):
        """
        Create
        """
        serializer = OrderUnassignCreateSerializer(data=request.data, context={
            'user': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
