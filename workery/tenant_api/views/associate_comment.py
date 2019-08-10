# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.associate_comment import AssociateCommentFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.associate import (
   CanListCreateAssociatePermission,
   CanRetrieveUpdateDestroyAssociatePermission
)
from tenant_api.serializers.associate_comment import AssociateCommentListCreateSerializer
from tenant_foundation.models import AssociateComment


class AssociateCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssociateCommentListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateAssociatePermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = AssociateComment.objects.all().order_by('-created_at').prefetch_related(
            'about',
            'comment',
        )

        # The following code will use the 'django-filter'
        filter = AssociateCommentFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = AssociateCommentListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
