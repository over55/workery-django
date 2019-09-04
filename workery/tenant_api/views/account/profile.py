# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.views import APIView
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.staff import (
   CanListCreateStaffPermission,
   CanRetrieveUpdateDestroyStaffPermission
)
from tenant_api.serializers.account.user_serializer import SharedUserRetrieveUpdateDestroySerializer
from tenant_foundation.models import Staff


class ProfileAPIView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
    )

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = SharedUserRetrieveUpdateDestroySerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
