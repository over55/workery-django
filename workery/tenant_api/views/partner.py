# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters import rest_framework as filters
from starterkit.drf.permissions import IsAuthenticatedAndIsActivePermission
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.permissions.partner import (
   CanListCreatePartnerPermission,
   CanRetrieveUpdateDestroyPartnerPermission
)
from tenant_api.serializers.partner import (
    PartnerListCreateSerializer,
    PartnerRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import Partner


class PartnerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PartnerListCreateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreatePartnerPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = Partner.objects.all().order_by('-created')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = PartnerListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PartnerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PartnerRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyPartnerPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        partner = get_object_or_404(Partner, pk=pk)
        self.check_object_permissions(request, partner)  # Validate permissions.
        serializer = PartnerRetrieveUpdateDestroySerializer(partner, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        partner = get_object_or_404(Partner, pk=pk)
        self.check_object_permissions(request, partner)  # Validate permissions.
        serializer = PartnerRetrieveUpdateDestroySerializer(partner, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        partner = get_object_or_404(Partner, pk=pk)
        self.check_object_permissions(request, partner)  # Validate permissions.
        partner.delete()
        return Response(data=[], status=status.HTTP_200_OK)


class PartnerCreateValidationAPIView(generics.CreateAPIView):
    serializer_class = PartnerListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreatePartnerPermission
    )

    def post(self, request, format=None):
        """
        Create
        """
        serializer = PartnerListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
