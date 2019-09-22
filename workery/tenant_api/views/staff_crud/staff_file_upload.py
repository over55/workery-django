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
from tenant_api.filters.staff_file_upload import StaffFileUploadFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.staff import (
   CanListCreateStaffPermission,
   CanRetrieveUpdateDestroyStaffPermission
)
from tenant_api.serializers.staff_crud.staff_file_upload import StaffFileUploadListCreateSerializer
from tenant_foundation.models import PrivateFileUpload


class StaffFileUploadListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StaffFileUploadListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateStaffPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = PrivateFileUpload.objects.all().order_by('-created_at').prefetch_related(
            'staff', 'created_by',
        )

        # The following code will use the 'django-filter'
        filter = StaffFileUploadFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = StaffFileUploadListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={}, status=status.HTTP_201_CREATED)


class StaffFileUploadArchiveAPIView(generics.DestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyStaffPermission
    )

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        staff = get_object_or_404(PrivateFileUpload, pk=pk)
        staff.is_archived = not staff.is_archived
        staff.last_modified_by = request.user
        staff.last_modified_from = client_ip
        staff.last_modified_from_is_public = is_routable
        staff.save()
        return Response(data={}, status=status.HTTP_200_OK)
