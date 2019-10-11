# -*- coding: utf-8 -*-
import django_filters
from ipware import get_client_ip
# from django_filters import rest_framework as filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_crud import WorkOrderInvoiceThirdSectionUpdateSerializer
from tenant_api.serializers.order_crud import WorkOrderInvoiceRetrieveSerializer
from tenant_foundation.models import WorkOrderInvoice


class WorkOrderInvoiceThirdSectionUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    @transaction.atomic
    def put(self, request, pk=None):
        """
        Update
        """
        client_ip, is_routable = get_client_ip(self.request)
        invoice = get_object_or_404(WorkOrderInvoice, order=pk)
        self.check_object_permissions(request, invoice.order)  # Validate permissions.
        write_serializer = WorkOrderInvoiceThirdSectionUpdateSerializer(invoice, data=request.data, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant,
        })
        write_serializer.is_valid(raise_exception=True)
        invoice = write_serializer.save()
        read_serializer = WorkOrderInvoiceRetrieveSerializer(invoice, many=False, context={
            'last_modified_by': request.user,
            'last_modified_from': client_ip,
            'last_modified_from_is_public': is_routable,
            'franchise': request.tenant,
        })
        return Response(read_serializer.data, status=status.HTTP_200_OK)
