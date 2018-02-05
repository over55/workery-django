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
from tenant_api.permissions.order import (
   CanListCreateOrderPermission,
   CanRetrieveUpdateDestroyOrderPermission
)
from tenant_api.serializers.order import (
    OrderListCreateSerializer,
    OrderRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import Order


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderListCreateSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateOrderPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = Order.objects.all().order_by('-created')
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = OrderListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyOrderPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = OrderRetrieveUpdateDestroySerializer(order, many=False)
        # queryset = serializer.setup_eager_loading(self, queryset)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = OrderRetrieveUpdateDestroySerializer(order, data=request.data, context={
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
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        order.delete()
        return Response(data=[], status=status.HTTP_200_OK)
