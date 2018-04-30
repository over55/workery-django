# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from starterkit.drf.permissions import IsAuthenticatedAndIsActivePermission
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from tenant_api.pagination import StandardResultsSetPagination
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
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateStaffPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = Staff.objects.all().order_by('-created')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = StaffListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StaffRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StaffRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
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

    def put(self, request, pk=None):
        """
        Update
        """
        staff = get_object_or_404(Staff, pk=pk)
        self.check_object_permissions(request, staff)  # Validate permissions.
        serializer = StaffRetrieveUpdateDestroySerializer(staff, data=request.data, context={
            'last_modified_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        staff = get_object_or_404(Staff, pk=pk)
        self.check_object_permissions(request, staff)  # Validate permissions.
        staff.delete()
        return Response(data=[], status=status.HTTP_200_OK)


class StaffCreateValidationAPIView(generics.ListCreateAPIView):
    serializer_class = StaffListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateStaffPermission
    )

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
