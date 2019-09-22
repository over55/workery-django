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
from tenant_api.filters.order_file_upload import WorkOrderFileUploadFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_crud.order_file_upload import WorkOrderFileUploadListCreateSerializer
from tenant_foundation.models import PrivateFileUpload


class WorkOrderFileUploadListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkOrderFileUploadListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = PrivateFileUpload.objects.all().order_by('-created_at').prefetch_related(
            'work_order', 'created_by',
        )

        # The following code will use the 'django-filter'
        filter = WorkOrderFileUploadFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = WorkOrderFileUploadListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={}, status=status.HTTP_201_CREATED)


class WorkOrderFileUploadArchiveAPIView(generics.DestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        work_order = get_object_or_404(PrivateFileUpload, pk=pk)
        work_order.is_archived = not work_order.is_archived
        work_order.last_modified_by = request.user
        work_order.last_modified_from = client_ip
        work_order.last_modified_from_is_public = is_routable
        work_order.save()
        return Response(data={}, status=status.HTTP_200_OK)
