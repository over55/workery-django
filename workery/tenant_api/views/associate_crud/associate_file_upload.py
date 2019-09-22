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
from tenant_api.filters.associate_file_upload import AssociateFileUploadFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.associate import (
   CanListCreateAssociatePermission,
   CanRetrieveUpdateDestroyAssociatePermission
)
from tenant_api.serializers.associate_crud.associate_file_upload import AssociateFileUploadListCreateSerializer
from tenant_foundation.models import PrivateFileUpload


class AssociateFileUploadListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssociateFileUploadListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateAssociatePermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = PrivateFileUpload.objects.all().order_by('-created_at').prefetch_related(
            'associate', 'created_by',
        )

        # The following code will use the 'django-filter'
        filter = AssociateFileUploadFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = AssociateFileUploadListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={}, status=status.HTTP_201_CREATED)


class AssociateFileUploadArchiveAPIView(generics.DestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyAssociatePermission
    )

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        associate = get_object_or_404(PrivateFileUpload, pk=pk)
        associate.is_archived = not associate.is_archived
        associate.last_modified_by = request.user
        associate.last_modified_from = client_ip
        associate.last_modified_from_is_public = is_routable
        associate.save()
        return Response(data={}, status=status.HTTP_200_OK)
