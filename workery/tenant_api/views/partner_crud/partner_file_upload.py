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
from tenant_api.filters.partner_file_upload import PartnerFileUploadFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.partner import (
   CanListCreatePartnerPermission,
   CanRetrieveUpdateDestroyPartnerPermission
)
from tenant_api.serializers.partner_crud.partner_file_upload import PartnerFileUploadListCreateSerializer
from tenant_foundation.models import PrivateFileUpload


class PartnerFileUploadListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PartnerFileUploadListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreatePartnerPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = PrivateFileUpload.objects.all().order_by('-created_at').prefetch_related(
            'partner', 'created_by',
        )

        # The following code will use the 'django-filter'
        filter = PartnerFileUploadFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = PartnerFileUploadListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={}, status=status.HTTP_201_CREATED)


class PartnerFileUploadArchiveAPIView(generics.DestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyPartnerPermission
    )

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        partner = get_object_or_404(PrivateFileUpload, pk=pk)
        partner.is_archived = not partner.is_archived
        partner.last_modified_by = request.user
        partner.last_modified_from = client_ip
        partner.last_modified_from_is_public = is_routable
        partner.save()
        return Response(data={}, status=status.HTTP_200_OK)
