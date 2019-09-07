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
from tenant_api.serializers.staff import (
    StaffListCreateSerializer,
    StaffRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import Staff


class StaffListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = StaffListCreateSerializer
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
        # Fetch all the queries.
        queryset = Staff.objects.all().order_by('-created').prefetch_related(
            'owner',
        )

        # The following code will use the 'django-filter'
        filter = StaffFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = StaffListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StaffRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StaffRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyStaffPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        staff = get_object_or_404(Staff, pk=pk)
        self.check_object_permissions(request, staff)  # Validate permissions.
        serializer = StaffRetrieveUpdateDestroySerializer(staff, many=False)
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
        staff = get_object_or_404(Staff, pk=pk)
        self.check_object_permissions(request, staff)  # Validate permissions.
        serializer = StaffRetrieveUpdateDestroySerializer(staff, data=request.data, context={
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
        client_ip, is_routable = get_client_ip(self.request)
        staff = get_object_or_404(Staff, pk=pk)
        self.check_object_permissions(request, staff)  # Validate permissions.
        staff.owner.is_active = False
        staff.owner.save()
        staff.is_archived = False
        staff.last_modified_by = request.user
        staff.last_modified_from = client_ip
        staff.last_modified_from_is_public = is_routable
        staff.save()
        return Response(data=[], status=status.HTTP_200_OK)


class StaffCreateValidationAPIView(generics.ListCreateAPIView):
    serializer_class = StaffListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateStaffPermission
    )

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        serializer = StaffListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
