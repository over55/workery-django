# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.pagination import TinyResultsSetPagination
from shared_foundation.models.franchise import SharedFranchise
from shared_api.serializers.franchise_serializers import (
    SharedFranchiseListCreateSerializer, SharedFranchiseRetrieveSerializer, SharedFranchiseUpdateSerializer
)


class SharedFranchiseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SharedFranchiseListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        """
        Overriding the initial queryset
        """
        queryset = SharedFranchise.objects.all().exclude(schema_name="public").order_by('name')

        # Set up eager loading to avoid N+1 selects
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)
        return queryset

    # def post(self, request, format=None):
    #     """
    #     Create
    #     """
    #     serializer = SharedFranchiseListCreateSerializer(data=request.data, context={
    #         'created_by': request.user
    #     })
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)






class SharedFranchiseRetrieveDeleteDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        order = get_object_or_404(SharedFranchise, pk=pk)
        self.check_object_permissions(request, order)  # Validate permissions.
        serializer = SharedFranchiseRetrieveSerializer(order, many=False)
        # queryset = serializer.setup_eager_loading(self, queryset)
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
        associate = get_object_or_404(SharedFranchise, pk=pk)
        self.check_object_permissions(request, associate)  # Validate permissions.
        write_serializer = SharedFranchiseUpdateSerializer(associate, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable
        })
        write_serializer.is_valid(raise_exception=True)
        associate = write_serializer.save()
        read_serializer = SharedFranchiseRetrieveSerializer(associate, many=False, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)


class SharedFranchiseCreateValidationAPIView(generics.CreateAPIView):
    """
    API endpoint strictly used for POST creation validations of the
    `SharedFranchise` model before an actual POST create API call is made.
    """
    serializer_class = SharedFranchiseListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    def post(self, request, format=None):
        """
        Create
        """
        serializer = SharedFranchiseListCreateSerializer(data=request.data, context={
            'created_by': request.user,
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
