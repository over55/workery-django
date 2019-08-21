# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.associate import (
   CanListCreateAssociatePermission,
   CanRetrieveUpdateDestroyAssociatePermission
)
from tenant_api.filters.associate import AssociateFilter
from tenant_api.serializers.associate import (
    AssociateListCreateSerializer,
    AssociateRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import Associate
from django.db import transaction


class AssociateMetricsUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssociateRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyAssociatePermission
    )

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        associate = get_object_or_404(Associate, pk=pk)
        self.check_object_permissions(request, associate)  # Validate permissions.
        serializer = AssociateRetrieveUpdateDestroySerializer(associate, many=False)
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
        associate = get_object_or_404(Associate, pk=pk)
        self.check_object_permissions(request, associate)  # Validate permissions.
        serializer = AssociateRetrieveUpdateDestroySerializer(associate, data=request.data, context={
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
        associate = get_object_or_404(Associate, pk=pk)
        self.check_object_permissions(request, associate)  # Validate permissions.
        associate.delete()
        return Response(data=[], status=status.HTTP_200_OK)


class AssociateCreateValidationAPIView(generics.CreateAPIView):
    """
    API endpoint strictly used for POST creation validations of the associate
    model before an actual POST create API call is made.
    """
    serializer_class = AssociateListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateAssociatePermission
    )
    def post(self, request, format=None):
        """
        Create
        """
        serializer = AssociateListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
