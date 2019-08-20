# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import filters
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.filters.staff import StaffFilter
from tenant_api.permissions.staff import (
   CanListCreateStaffPermission,
   CanRetrieveUpdateDestroyStaffPermission
)
from tenant_api.serializers.staff_crud import StaffAddressUpdateSerializer
from tenant_api.serializers.staff import StaffRetrieveUpdateDestroySerializer
from tenant_foundation.models import Staff


class StaffAddressUpdateAPIView(generics.UpdateAPIView):
    serializer_class = StaffAddressUpdateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyStaffPermission
    )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        staff = get_object_or_404(Staff, pk=pk)
        self.check_object_permissions(request, staff)  # Validate permissions.
        write_serializer = StaffAddressUpdateSerializer(staff, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        write_serializer.is_valid(raise_exception=True)
        staff = write_serializer.save()
        read_serializer = StaffRetrieveUpdateDestroySerializer(staff, many=False, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)
