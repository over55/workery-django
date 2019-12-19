# -*- coding: utf-8 -*-
from ipware import get_client_ip
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.unified_search_item import UnifiedSearchItemFilter
from tenant_api.pagination import TinyResultsSetPagination
# from tenant_api.permissions.tag import (
#    CanListCreateUnifiedSearchItemPermission,
#    CanRetrieveUpdateDestroyUnifiedSearchItemPermission
# )
from tenant_api.serializers.unified_search_item import UnifiedSearchItemListSerializer
from tenant_foundation.models import UnifiedSearchItem


class UnifiedSearchItemListAPIView(generics.ListAPIView):
    serializer_class = UnifiedSearchItemListSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        # CanListCreateUnifiedSearchItemPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = UnifiedSearchItem.objects.all().order_by('-last_modified_at')

        # The following code will use the 'django-filter'
        filter = UnifiedSearchItemFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset
