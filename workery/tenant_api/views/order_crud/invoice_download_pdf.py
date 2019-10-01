# -*- coding: utf-8 -*-
"""
The following code is responsible for submitting to our `invoicebuilder` API
the details of our invoice and receive a binary file which we will return
to the user as a PDF.

Special thanks to the following resources:
* https://stackoverflow.com/a/49652011
"""
import grpc
import django_filters
from ipware import get_client_ip
# from django_filters import rest_framework as filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.renderers import BaseRenderer
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_api.protos import invoice_pb2
from tenant_api.protos import invoice_pb2_grpc
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.order_crud import WorkOrderInvoiceRetrieveSerializer
from tenant_foundation.models import WorkOrderInvoice


class BinaryFileRenderer(BaseRenderer):
    media_type = 'application/octet-stream'
    format = None
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

def save_chunks_to_file(chunks, filename):
    """
    Utility function will take the chunks recieved from the remote server
    and save the chunks to a local file. Special thanks to the following:
    https://github.com/gooooloo/grpc-file-transfer
    """
    with open(filename, 'wb') as f:
        for chunk in chunks:
            f.write(chunk.buffer)


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
        #TODO: Update our invoice with our latest data before we build it.
        self.check_object_permissions(request, invoice.order)  # Validate permissions.

        with grpc.insecure_channel('localhost:50051') as channel: #TODO: MAKE INTO CONSTANT
            stub = invoice_pb2_grpc.InvoiceBuilderStub(channel)
            response = stub.GeneratePDF(invoice_pb2.GeneratePDFRequest( #TODO: Get from our `invoice` object in Django.
                invoiceId='1',
                invoiceDate='2019-01-01',
                associateName='Bob the Builder11111111111',
                associateTelephone='(123) 456-7898',
                clientName = 'John Smith11111111111111111111111111111122222222222222222222222',
                clientAddress = '123-321 Simple Road, London, Ontario, Canada, N6J 4X4',
                clientTelephone = '(999) 999-9999',
                clientEmail = 'john@smith.com',
                line01Quantity = '1',
                line01Description = 'This is a somesort of description.12345678901',
                line01Price = '$100.00',
                line01Amount = '$100.00',
                line02Quantity = '',
                line02Description = '',
                line02Price = '',
                line02Amount = '',
                line03Quantity = '',
                line03Description = '',
                line03Price = '',
                line03Amount = '',
                line04Quantity = '',
                line04Description = '',
                line04Price = '',
                line04Amount = '',
                line05Quantity = '',
                line05Description = '',
                line05Price = '',
                line05Amount = '',
                line06Quantity = '',
                line06Description = '',
                line06Price = '',
                line06Amount = '',
                line07Quantity = '',
                line07Description = '',
                line07Price = '',
                line07Amount = '',
                line08Quantity = '',
                line08Description = '',
                line08Price = '',
                line08Amount = '',
                line09Quantity = '',
                line09Description = '',
                line09Price = '',
                line09Amount = '',
                line10Quantity = '',
                line10Description = '',
                line10Price = '',
                line10Amount = '',
                line11Quantity = '',
                line11Description = '',
                line11Price = '',
                line11Amount = '',
                line12Quantity = '',
                line12Description = '',
                line12Price = '',
                line12Amount = '',
                line13Quantity = '',
                line13Description = '',
                line13Price = '',
                line13Amount = '',
                line14Quantity = '',
                line14Description = '',
                line14Price = '',
                line14Amount = '',
                line15Quantity = '',
                line15Description = '',
                line15Price = '',
                line15Amount = '',
                invoiceQuoteDays = '15',
                invoiceAssociateTax = '1234567-R12311',
                invoiceQuoteDate = '2019-01-01',
                invoiceCustomersApproval = 'John Smith1111111111',
                line01Notes = 'This is somesort of text.1111111111111111111111111111111111111111111111111111111',
                line02Notes = '11111111111111111111111111111111111111111',
                totalLabour = '$100.00',
                totalMaterials = '$100.00',
                wasteRemoval = '',
                subTotal = '$100.00',
                tax = '$13.00',
                total = '$130.00',
                grandTotal = '$130.00',
                paymentAmount = '$130.00',
                paymentDate = '2019-01-01',
                cash = 'X',
                cheque = '',
                debit = '',
                credit = '',
                other = '',
                clientSignature = 'John Smith6666666666666666666666666666666666666',
                associateSignDate = '2019-01-01',
                associateSignature = 'Bob the Builder11111111111111',
                workOrderId = '1234567',
            ))
            save_chunks_to_file(response, "media/sample.pdf") #TODO: Replace with custom file name.
            with open('media/sample.pdf', 'rb') as report: #TODO: Replace with custom file name.
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
