# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.vehicle_type import VehicleTypeFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.tag import (
   CanListCreateTagPermission,
   CanRetrieveUpdateDestroyTagPermission
)
from tenant_api.serializers.vehicle_type import (
    VehicleTypeListCreateSerializer,
    VehicleTypeRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import VehicleType


class VehicleTypeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VehicleTypeListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateTagPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = VehicleType.objects.all().order_by('text')

        # The following code will use the 'django-filter'
        filter = VehicleTypeFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = VehicleTypeListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VehicleTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleTypeRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyTagPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        vt = get_object_or_404(VehicleType, pk=pk)
        self.check_object_permissions(request, vt)  # Validate permissions.
        serializer = VehicleTypeRetrieveUpdateDestroySerializer(vt, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        vt = get_object_or_404(VehicleType, pk=pk)
        self.check_object_permissions(request, vt)  # Validate permissions.
        serializer = VehicleTypeRetrieveUpdateDestroySerializer(vt, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        client_ip, is_routable = get_client_ip(self.request)
        vt = get_object_or_404(VehicleType, pk=pk)
        self.check_object_permissions(request, vt)  # Validate permissions.
        vt.is_archived = True
        vt.last_modified_by = request.user
        vt.last_modified_from = client_ip
        vt.last_modified_from_is_public = is_routable
        vt.save()
        return Response(data=[], status=status.HTTP_200_OK)
