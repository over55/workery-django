# -*- coding: utf-8 -*-
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.filters.insurance_requirement import InsuranceRequirementFilter
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.insurance_requirement import (
   CanListCreateInsuranceRequirementPermission,
   CanRetrieveUpdateDestroyInsuranceRequirementPermission
)
from tenant_api.serializers.insurance_requirement import (
    InsuranceRequirementListCreateSerializer,
    InsuranceRequirementRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import InsuranceRequirement


class InsuranceRequirementListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InsuranceRequirementListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanListCreateInsuranceRequirementPermission
    )

    def get_queryset(self):
        """
        List
        """
        # Fetch all the queries.
        queryset = InsuranceRequirement.objects.all().order_by('text')

        # The following code will use the 'django-filter'
        filter = InsuranceRequirementFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs

        # Return our filtered list.
        return queryset

    def post(self, request, format=None):
        """
        Create
        """
        serializer = InsuranceRequirementListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InsuranceRequirementRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InsuranceRequirementRetrieveUpdateDestroySerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyInsuranceRequirementPermission
    )

    def get(self, request, pk=None):
        """
        Retrieve
        """
        insurance_requirement = get_object_or_404(InsuranceRequirement, pk=pk)
        self.check_object_permissions(request, insurance_requirement)  # Validate permissions.
        serializer = InsuranceRequirementRetrieveUpdateDestroySerializer(insurance_requirement, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        """
        Update
        """
        insurance_requirement = get_object_or_404(InsuranceRequirement, pk=pk)
        self.check_object_permissions(request, insurance_requirement)  # Validate permissions.
        serializer = InsuranceRequirementRetrieveUpdateDestroySerializer(insurance_requirement, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        Delete
        """
        insurance_requirement = get_object_or_404(InsuranceRequirement, pk=pk)
        self.check_object_permissions(request, insurance_requirement)  # Validate permissions.
        insurance_requirement.delete()
        return Response(data=[], status=status.HTTP_200_OK)
