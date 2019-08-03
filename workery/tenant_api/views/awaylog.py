# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils import timezone
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.awayLog import AwayLogFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.awaylog import (
   CanListCreateAwayLogPermission,
   CanRetrieveUpdateDestroyAwayLogPermission
)
from tenant_api.serializers.awaylog import (
    AwayLogListCreateSerializer,
    AwayLogRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import (
    AwayLog,
    Associate,
    AssociateComment,
    Comment
)



class AwayLogListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AwayLogListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateAwayLogPermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)

    def get_queryset(self):
        """
        List
        """
        queryset = AwayLog.objects.all().order_by('-created').prefetch_related(
            'associate',
        )

        # The following code will use the 'django-filter'
        filter = AwayLogFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = AwayLogListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AwayLogRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AwayLogRetrieveUpdateDestroySerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyAwayLogPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        obj = get_object_or_404(AwayLog, pk=pk)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = AwayLogRetrieveUpdateDestroySerializer(obj, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        obj = get_object_or_404(AwayLog, pk=pk)
        self.check_object_permissions(request, obj)  # Validate permissions.
        serializer = AwayLogRetrieveUpdateDestroySerializer(obj, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        #-----------------------------
        # Change the `AWayLog` object.
        #-----------------------------
        # Lookup the object or give a 404 error.
        obj = get_object_or_404(AwayLog, pk=pk)
        self.check_object_permissions(request, obj)  # Validate permissions.
        obj.was_deleted = True
        obj.save()
        obj.associate.away_log = None
        obj.associate.save()

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        utc_dt = timezone.now()
        current_dt = request.tenant.to_tenant_dt(utc_dt)
        # Create our comment text.
        comment_text = "System Note: Staff member ID #" + str(request.user.id)
        comment_text += " has set the Associate to no longer be away on " +  str(current_dt) + ". "

        # Create our object.
        comment_obj = Comment.objects.create(
            created_by = request.user,
            last_modified_by = request.user,
            text=comment_text,
            # created_from = self.context['created_from'],
            # created_from_is_public = self.context['created_from_is_public']
        )
        associate_comment = AssociateComment.objects.create(
            about=obj.associate,
            comment=comment_obj,
        )

        #-----------------------------
        # Return our `AwayLog` object.
        #-----------------------------
        # Return our result.
        return Response(data=[], status=status.HTTP_200_OK)
