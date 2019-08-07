# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.partner import PartnerFilter
from tenant_api.pagination import TinyResultsSetPagination
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
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreatePartnerPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = Partner.objects.all().order_by('-created').prefetch_related(
            'owner',
        )

        # The following code will use the 'django-filter'
        filter = PartnerFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    @transaction.atomic
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
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyPartnerPermission
    )

    @transaction.atomic
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

    @transaction.atomic
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

    @transaction.atomic
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
