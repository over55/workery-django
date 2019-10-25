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
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.associate_operations import AssociateUpgradeOperationSerializer
from tenant_api.serializers.associate import AssociateRetrieveUpdateDestroySerializer


class AssociateUprageOperationAPIView(generics.CreateAPIView):
    serializer_class = AssociateUpgradeOperationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateWorkOrderPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        client_ip, is_routable = get_client_ip(self.request)
        write_serializer = AssociateUpgradeOperationSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
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
