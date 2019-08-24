# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.associate import (
   CanListCreateAssociatePermission,
   CanRetrieveUpdateDestroyAssociatePermission
)
from tenant_api.filters.associate import AssociateFilter
from tenant_api.serializers.task_crud import TaskItemAvailableAssociateListCreateSerializer
from tenant_foundation.models import Associate, TaskItem, ActivitySheetItem
from django.db import transaction


class TaskItemAvailableAssociateListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskItemAvailableAssociateListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateAssociatePermission
    )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    # search_fields = ('@given_name', '@middle_name', '@last_name', '@email', 'telephone', '@wsib_number')

    @transaction.atomic
    def get_queryset(self):
        """
        List
        """
        taskItemId = self.kwargs.get('pk', None)
        task_item = TaskItem.objects.filter(id=taskItemId).first()

        # (a) Find all the unique associates that match the job skill criteria
        #     for the job.
        # (b) Find all the unique associates which do not have any activity
        #     sheet items created previously.
        # (c) FInd all unique associates which have active accounts.
        # (d) If an Associate has an active Announcement attached to them,
        #     they should be uneligible for a job.
        skill_set_pks = None
        try:
            skill_set_pks = task_item.job.skill_sets.values_list('pk', flat=True)
            activity_sheet_associate_pks = ActivitySheetItem.objects.filter(
                job=task_item.job
            ).values_list('associate_id', flat=True)
            return Associate.objects.filter(
               Q(skill_sets__in=skill_set_pks) &
               ~Q(id__in=activity_sheet_associate_pks) &
               Q(owner__is_active=True) &
               Q(
                   Q(away_log__isnull=True)|
                   Q(away_log__start_date__gt=timezone.now()) # (*)
               )
            ).distinct()

            # (*) - If tassociates vacation did not start today then allow
            #       the associate to be listed as available in the list.
        except Exception as e:
            available_associates = None
            print("available_for_task_item_filtering |", e)
        return Associate.objects.none()

        # # Fetch all the queries.
        # queryset = Associate.objects.all().order_by('last_name').prefetch_related(
        #     'owner',
        #     # 'created_by',
        #     # 'last_modified_by',
        #     'tags',
        #     'skill_sets',
        #     # 'vehicle_types',
        #     # 'comments',
        #     # 'insurance_requirements',
        # )
        #
        # # The following code will use the 'django-filter'
        # filter = AssociateFilter(self.request.GET, queryset=queryset)
        # queryset = filter.qs
        #
        # # Return our filtered list.
        # return queryset

    @transaction.atomic
    def post(self, request, format=None):
        """
        Create
        """
        client_ip, is_routable = get_client_ip(self.request)
        serializer = TaskItemAvailableAssociateListCreateSerializer(data=request.data, context={
            'created_by': request.user,
            'created_from': client_ip,
            'created_from_is_public': is_routable,
            'franchise': request.tenant
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
