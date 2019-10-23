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
from tenant_api.filters.task_item import TaskItemFilter
from tenant_api.permissions.task_item import CanListCreateTaskItemPermission
from tenant_api.serializers.task_crud import TaskItemListSerializer
from tenant_foundation.models import TaskItem


class TaskItemListPIView(generics.ListAPIView):
    serializer_class = TaskItemListSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    # search_fields = ('@given_name', '@middle_name', '@last_name', '@email', 'telephone',)

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = TaskItem.objects.all().order_by('-created_at').prefetch_related(
            'job',
            'job__associate',
            'job__associate__away_log',
            'job__customer',
            'ongoing_job',
            'created_by',
            'last_modified_by'
        )

        # The following code will filter out the tasks based on user role. It's
        # important to note this code is used to handle permission handling
        # based on roles.
        if self.request.user.is_staff():
            pass
        elif self.request.user.is_associate():
            queryset = queryset.filter(job__associate__owner=self.request.user)
        else:
            queryset = TaskItem.objects.none()

        # The following code will use the 'django-filter'
        filter = TaskItemFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset
