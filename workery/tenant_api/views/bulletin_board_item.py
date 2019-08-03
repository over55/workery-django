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
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.bulletin_board_item import (
   CanListCreateBulletinBoardItemPermission,
   CanRetrieveUpdateDestroyBulletinBoardItemPermission
)
from tenant_api.serializers.bulletin_board_item import (
    BulletinBoardItemListCreateSerializer,
    BulletinBoardItemRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import BulletinBoardItem, Customer


class BulletinBoardItemListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BulletinBoardItemListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateBulletinBoardItemPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = BulletinBoardItem.objects.all().order_by('-created')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = BulletinBoardItemListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BulletinBoardItemRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BulletinBoardItemRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyBulletinBoardItemPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        tag = get_object_or_404(BulletinBoardItem, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = BulletinBoardItemRetrieveUpdateDestroySerializer(tag, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        tag = get_object_or_404(BulletinBoardItem, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        serializer = BulletinBoardItemRetrieveUpdateDestroySerializer(tag, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        tag = get_object_or_404(BulletinBoardItem, pk=pk)
        self.check_object_permissions(request, tag)  # Validate permissions.
        tag.delete()
        return Response(data=[], status=status.HTTP_200_OK)
