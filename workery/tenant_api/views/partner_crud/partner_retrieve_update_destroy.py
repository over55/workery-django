# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.partner import PartnerFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.partner import (
   CanListCreatePartnerPermission,
   CanRetrieveUpdateDestroyPartnerPermission
)
from tenant_api.serializers.partner_crud import PartnerRetrieveUpdateDestroySerializer
from tenant_foundation.models import Partner


class PartnerRetrieveUpdateDestroyV2APIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PartnerRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyPartnerPermission
    )

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        partner = get_object_or_404(Partner, pk=pk)
        self.check_object_permissions(request, partner)  # Validate permissions.
        serializer = PartnerRetrieveUpdateDestroySerializer(partner, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        partner = get_object_or_404(Partner, pk=pk)
        self.check_object_permissions(request, partner)  # Validate permissions.
        serializer = PartnerRetrieveUpdateDestroySerializer(partner, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk=None):
        """
        Delete
        """
        partner = get_object_or_404(Partner, pk=pk)
        self.check_object_permissions(request, partner)  # Validate permissions.
        partner.delete()
        return Response(data=[], status=status.HTTP_200_OK)
