# -*- coding: utf-8 -*-
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from starterkit.drf.permissions import IsAuthenticatedAndIsActivePermission
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.permissions.associate import (
   CanListCreateAssociatePermission,
   CanRetrieveUpdateDestroyAssociatePermission
)
from tenant_api.serializers.associate import (
    AssociateListCreateSerializer,
    AssociateRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import Associate


class AssociateListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssociateListCreateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateAssociatePermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('given_name', 'middle_name', 'last_name', 'email', 'telephone',)

    def get_queryset(self):
        """
        List
        """
        queryset = Associate.objects.all().order_by('-created')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = AssociateListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AssociateRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssociateRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyAssociatePermission
    )

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

    def put(self, request, pk=None):
        """
        Update
        """
        associate = get_object_or_404(Associate, pk=pk)
        self.check_object_permissions(request, associate)  # Validate permissions.
        serializer = AssociateRetrieveUpdateDestroySerializer(associate, data=request.data, context={
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
        associate = get_object_or_404(Associate, pk=pk)
        self.check_object_permissions(request, associate)  # Validate permissions.
        associate.delete()
        return Response(data=[], status=status.HTTP_200_OK)
