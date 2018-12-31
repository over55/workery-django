# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.permissions.partner import (
   CanListCreatePartnerPermission,
   CanRetrieveUpdateDestroyPartnerPermission
)
from tenant_api.serializers.partner_comment import (
    PartnerListCreateSerializer,
)
from tenant_foundation.models import Partner


class PartnerCommentListCreateAPIView(generics.ListCreateAPIView):
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
        serializer = PartnerListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
