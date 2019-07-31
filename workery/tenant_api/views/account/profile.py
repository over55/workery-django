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


class ProfileAPIView(generics.ListCreateAPIView):
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
        # client_ip, is_routable = get_client_ip(self.request)
        # serializer = StaffListCreateSerializer(data=request.data, context={
        #     'created_by': request.user,
        #     'created_from': client_ip,
        #     'created_from_is_public': is_routable,
        #     'franchise': request.tenant
        # })
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
