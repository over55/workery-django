# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from starterkit.drf.permissions import IsAuthenticatedAndIsActivePermission
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.permissions.awaylog import (
   CanListCreateAwayLogPermission,
   CanRetrieveUpdateDestroyAwayLogPermission
)
from tenant_api.serializers.awaylog import (
    AwayLogListCreateSerializer,
    AwayLogRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import AwayLog


class AwayLogListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AwayLogListCreateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateAwayLogPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = AwayLog.objects.all().order_by('text')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = AwayLogListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AwayLogRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AwayLogRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyAwayLogPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        obj = get_object_or_404(AwayLog, pk=pk)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = AwayLogRetrieveUpdateDestroySerializer(obj, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        obj = get_object_or_404(AwayLog, pk=pk)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = AwayLogRetrieveUpdateDestroySerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        obj = get_object_or_404(AwayLog, pk=pk)
        self.check_object_permissions(request, obj)  # Validate permissions.
        obj.was_deleted = True
        obj.save()
        obj.associate.away_log = None
        obj.associate.save()
        return Response(data=[], status=status.HTTP_200_OK)
