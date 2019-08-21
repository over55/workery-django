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
from tenant_api.serializers.associate import AssociateRetrieveUpdateDestroySerializer
from tenant_api.serializers.associate_crud import AssociateMetricsUpdateSerializer
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
    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        associate = get_object_or_404(Associate, pk=pk)
        self.check_object_permissions(request, associate)  # Validate permissions.
        write_serializer = AssociateMetricsUpdateSerializer(associate, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        write_serializer.is_valid(raise_exception=True)
        associate = write_serializer.save()
        read_serializer = AssociateRetrieveUpdateDestroySerializer(associate, many=False, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)
