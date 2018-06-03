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
from tenant_api.permissions.public_image_upload import (
   CanListCreatePublicImageUploadPermission,
   CanRetrieveUpdateDestroyPublicImageUploadPermission
)
from tenant_api.serializers.public_image_upload import (
    PublicImageUploadListCreateSerializer
)
from tenant_foundation.models import PublicImageUpload


class PublicImageUploadListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PublicImageUploadListCreateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (
        # permissions.IsAuthenticated,
        # IsAuthenticatedAndIsActivePermission,
        # CanListCreatePublicImageUploadPermission
    )

    def get_queryset(self):
        """
        List
        """
        queryset = PublicImageUpload.objects.all().order_by('-id')
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        # Get the users IP.
        client_ip, is_routable = get_client_ip(self.request)

        # Input the POST data into our serializer to create our image.
        serializer = PublicImageUploadListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
