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

from tenant_api.serializers.account.associate_profile_serializer import AssociateProfileSerializer
from tenant_api.serializers.account.staff_profile_serializer import StaffProfileSerializer
from tenant_foundation.models import Associate


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
        serializer = None
        if request.user.is_associate():
            associate = Associate.objects.get_associate_with_user_id(request.user.id)
            serializer = AssociateProfileSerializer(associate)
        else:
            serializer = StaffProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
