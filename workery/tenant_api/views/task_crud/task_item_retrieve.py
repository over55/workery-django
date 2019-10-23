# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import filters
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.filters.staff import StaffFilter
from tenant_api.permissions.task_item import (
   CanListCreateTaskItemPermission,
   CanRetrieveUpdateDestroyTaskItemPermission
)
from tenant_api.serializers.task_crud import TaskItemRetrieveSerializer
from tenant_foundation.models import TaskItem


class TaskItemRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskItemRetrieveSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyTaskItemPermission
    )

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        task_item = get_object_or_404(TaskItem, pk=pk)
        self.check_object_permissions(request, task_item)  # Validate permissions.
        serializer = TaskItemRetrieveSerializer(task_item, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    # @transaction.atomic
    # def put(self, request, pk=None):
    #     """
    #     Update
    #     """
    #     client_ip, is_routable = get_client_ip(self.request)
    #     task_item = get_object_or_404(Associate, pk=pk)
    #     self.check_object_permissions(request, task_item)  # Validate permissions.
    #     serializer = AssociateRetrieveUpdateDestroySerializer(task_item, data=request.data, context={
    #         'last_modified_by': request.user,
    #         'last_modified_from': client_ip,
    #         'last_modified_from_is_public': is_routable,
    #         'franchise': request.tenant
    #     })
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # @transaction.atomic
    # def delete(self, request, pk=None):
    #     """
    #     Delete
    #     """
    #     task_item = get_object_or_404(Associate, pk=pk)
    #     self.check_object_permissions(request, task_item)  # Validate permissions.
    #     task_item.delete()
    #     return Response(data=[], status=status.HTTP_200_OK)
