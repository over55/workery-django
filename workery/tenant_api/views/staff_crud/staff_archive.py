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
from tenant_api.serializers.staff_crud import StaffAccountUpdateSerializer
from tenant_api.serializers.staff import StaffRetrieveUpdateDestroySerializer
from tenant_foundation.models import Staff


class StaffArchiveAPIView(generics.DestroyAPIView):
    serializer_class = StaffAccountUpdateSerializer
    pagination_class = TinyResultsSetPagination
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
        staff = get_object_or_404(Staff, pk=pk)
        self.check_object_permissions(request, staff)  # Validate permissions.
        staff.owner.is_active = not staff.owner.is_active
        staff.owner.save()
        staff.is_archived = not staff.is_archived 
        staff.last_modified_by = request.user
        staff.last_modified_from = client_ip
        staff.last_modified_from_is_public = is_routable
        staff.save()
        return Response(data=[], status=status.HTTP_200_OK)
