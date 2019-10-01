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
from tenant_api.serializers.order_crud import WorkOrderInvoiceRetrieveSerializer
from tenant_foundation.models import WorkOrderInvoice


from rest_framework.renderers import BaseRenderer
class BinaryFileRenderer(BaseRenderer):
    media_type = 'application/octet-stream'
    format = None
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class WorkOrderInvoiceDownloadPDFAPIView(generics.RetrieveAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    renderer_classes=(BinaryFileRenderer,)

    def get(self, request, pk=None):
        """
        Retrieve
        """
        invoice = get_object_or_404(WorkOrderInvoice, order=pk)
        self.check_object_permissions(request, invoice.order)  # Validate permissions.

        with open('/Users/bmika/Developer/over55/workery-django/workery/media/sample.pdf', 'rb') as report:
            return Response(
                report.read(),
                headers={'Content-Disposition': 'attachment; filename="file.pdf"'},
                content_type='application/pdf'
            )

        # serializer = WorkOrderInvoiceRetrieveSerializer(invoice, many=False)
        # return Response(
        #     data=serializer.data,
        #     status=status.HTTP_200_OK
        # )
