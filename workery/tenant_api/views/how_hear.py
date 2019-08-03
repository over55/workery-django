# -*- coding: utf-8 -*-
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.how_hear import HowHearAboutUsItemFilter
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.permissions.tag import (
   CanListCreateTagPermission,
   CanRetrieveUpdateDestroyTagPermission
)
from tenant_api.serializers.how_hear import (
    HowHearAboutUsItemListCreateSerializer,
    HowHearAboutUsItemRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import HowHearAboutUsItem


class HowHearAboutUsItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = HowHearAboutUsItemListCreateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateTagPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = HowHearAboutUsItem.objects.all().order_by('text')

        # The following code will use the 'django-filter'
        filter = HowHearAboutUsItemFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = HowHearAboutUsItemListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HowHearAboutUsItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HowHearAboutUsItemRetrieveUpdateDestroySerializer
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
        tag = get_object_or_404(HowHearAboutUsItem, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = HowHearAboutUsItemRetrieveUpdateDestroySerializer(tag, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        tag = get_object_or_404(HowHearAboutUsItem, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = HowHearAboutUsItemRetrieveUpdateDestroySerializer(tag, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        tag = get_object_or_404(HowHearAboutUsItem, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        tag.delete()
        return Response(data=[], status=status.HTTP_200_OK)
