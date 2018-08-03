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
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateTagPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = VehicleType.objects.all().order_by('text')
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
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyTagPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        tag = get_object_or_404(VehicleType, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = VehicleTypeRetrieveUpdateDestroySerializer(tag, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        tag = get_object_or_404(VehicleType, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = VehicleTypeRetrieveUpdateDestroySerializer(tag, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        tag = get_object_or_404(VehicleType, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        tag.delete()
        return Response(data=[], status=status.HTTP_200_OK)
