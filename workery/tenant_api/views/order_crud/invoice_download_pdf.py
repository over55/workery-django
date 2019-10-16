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
import datetime
from ipware import get_client_ip
# from django_filters import rest_framework as filters
from django.conf import settings
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

    @transaction.atomic
    def get(self, request, pk=None):
        """
        Retrieve
        """
        invoice = get_object_or_404(WorkOrderInvoice, order=pk)
        order = invoice.order
        self.check_object_permissions(request, invoice.order)  # Validate permissions.

        # The following code will update the invoice with the latest date from
        # the work order.
        invoice.associate_name = str(order.associate)
        invoice.associate_telephone = str(order.associate.telephone)
        invoice.client_name = str(order.customer)
        invoice.clien_telephone = str(order.customer.telephone)
        #TODO: IMPLEMENT...
        invoice.save()
        # invoice.clientAddress = str(invoice.client_address),
        # invoice.clientTelephone = str(invoice.client_telephone),
        # invoice.clientEmail = str(invoice.client_email),
        # invoice.line01Quantity = str(invoice.line_01_qty),
        # invoice.line01Description = str(invoice.line_01_desc),
        # invoice.line01Price = str(invoice.line_01_price),
        # invoice.line01Amount = str(invoice.line_01_amount),
        # invoice.line02Quantity =  str(invoice.line_02_qty) if invoice.line_02_qty else "",
        # invoice.line02Description = str(invoice.line_02_desc) if invoice.line_02_qty else "",
        # invoice.line02Price = str(invoice.line_02_price) if invoice.line_02_qty else "",
        # invoice.line02Amount = str(invoice.line_02_amount) if invoice.line_02_qty else "",
        # invoice.line03Quantity = str(invoice.line_03_qty) if invoice.line_03_qty else "",
        # invoice.line03Description = str(invoice.line_03_desc) if invoice.line_03_qty else "",
        # invoice.line03Price = str(invoice.line_03_price) if invoice.line_03_qty else "",
        # invoice.line03Amount = str(invoice.line_03_amount) if invoice.line_03_qty else "",
        # invoice.line04Quantity = str(invoice.line_04_qty) if invoice.line_04_qty else "",
        # invoice.line04Description = str(invoice.line_04_desc) if invoice.line_04_qty else "",
        # invoice.line04Price = str(invoice.line_04_price) if invoice.line_04_qty else "",
        # invoice.line04Amount = str(invoice.line_04_amount) if invoice.line_04_qty else "",
        # invoice.line05Quantity = str(invoice.line_05_qty) if invoice.line_05_qty else "",
        # invoice.line05Description = str(invoice.line_05_desc) if invoice.line_05_qty else "",
        # invoice.line05Price = str(invoice.line_05_price) if invoice.line_05_qty else "",
        # invoice.line05Amount = str(invoice.line_05_amount) if invoice.line_05_qty else "",
        # invoice.line06Quantity = str(invoice.line_06_qty) if invoice.line_06_qty else "",
        # invoice.line06Description = str(invoice.line_06_desc) if invoice.line_06_qty else "",
        # invoice.line06Price = str(invoice.line_06_price) if invoice.line_06_qty else "",
        # invoice.line06Amount = str(invoice.line_06_amount) if invoice.line_06_qty else "",
        # invoice.line07Quantity = str(invoice.line_07_qty) if invoice.line_07_qty else "",
        # invoice.line07Description = str(invoice.line_07_desc) if invoice.line_07_qty else "",
        # invoice.line07Price = str(invoice.line_07_price) if invoice.line_07_qty else "",
        # invoice.line07Amount = str(invoice.line_07_amount) if invoice.line_07_qty else "",
        # invoice.line08Quantity = str(invoice.line_08_qty) if invoice.line_08_qty else "",
        # invoice.line08Description = str(invoice.line_08_desc) if invoice.line_08_qty else "",
        # invoice.line08Price = str(invoice.line_08_price) if invoice.line_08_qty else "",
        # invoice.line08Amount = str(invoice.line_08_amount) if invoice.line_08_qty else "",
        # invoice.line09Quantity = str(invoice.line_09_qty) if invoice.line_09_qty else "",
        # invoice.line09Description = str(invoice.line_09_desc) if invoice.line_09_qty else "",
        # invoice.line09Price = str(invoice.line_09_price) if invoice.line_09_qty else "",
        # invoice.line09Amount = str(invoice.line_09_amount) if invoice.line_09_qty else "",
        # invoice.line10Quantity = str(invoice.line_10_qty) if invoice.line_10_qty else "",
        # invoice.line10Description = str(invoice.line_10_desc) if invoice.line_10_qty else "",
        # invoice.line10Price = str(invoice.line_10_price) if invoice.line_10_qty else "",
        # invoice.line10Amount = str(invoice.line_10_amount) if invoice.line_10_qty else "",
        # invoice.line11Quantity = str(invoice.line_11_qty) if invoice.line_11_qty else "",
        # invoice.line11Description = str(invoice.line_11_desc) if invoice.line_11_qty else "",
        # invoice.line11Price = str(invoice.line_11_price) if invoice.line_11_qty else "",
        # invoice.line11Amount = str(invoice.line_11_amount) if invoice.line_11_qty else "",
        # invoice.line12Quantity = str(invoice.line_12_qty) if invoice.line_12_qty else "",
        # invoice. = str(invoice.line_12_desc) if invoice.line_12_qty else "",
        # invoice.line12Price = str(invoice.line_12_price) if invoice.line_12_qty else "",
        # invoice.line12Amount = str(invoice.line_12_amount) if invoice.line_12_qty else "",
        # invoice.line13Quantity = str(invoice.line_13_qty) if invoice.line_13_qty else "",
        # invoice.line13Description = str(invoice.line_13_desc) if invoice.line_13_qty else "",
        # invoice.line13Price = str(invoice.line_13_price) if invoice.line_13_qty else "",
        # invoice.line13Amount = str(invoice.line_13_amount) if invoice.line_13_qty else "",
        # line14Quantity = str(invoice.line_14_qty) if invoice.line_14_qty else "",
        # line14Description = str(invoice.line_14_desc) if invoice.line_14_qty else "",
        # line14Price = str(invoice.line_14_price) if invoice.line_14_qty else "",
        # line14Amount = str(invoice.line_14_amount) if invoice.line_14_qty else "",
        # line15Quantity = str(invoice.line_15_qty) if invoice.line_15_qty else "",
        # line15Description = str(invoice.line_15_desc) if invoice.line_15_qty else "",
        # line15Price = str(invoice.line_15_price) if invoice.line_15_qty else "",
        # line15Amount = str(invoice.line_15_amount) if invoice.line_15_qty else "",
        # invoiceQuoteDays = str(invoice.invoice_quote_days),
        # invoiceAssociateTax = str(invoice.invoice_associate_tax),
        # invoiceQuoteDate = invoice.invoice_quote_date.strftime('%B %d, %Y'),
        # invoiceCustomersApproval = str(invoice.invoice_customers_approval),
        # line01Notes = str(invoice.line_01_notes),
        # line02Notes = str(invoice.line_02_notes) if invoice.line_02_notes else "",
        # totalLabour = str(invoice.total_labour),
        # totalMaterials = str(invoice.total_materials),
        # wasteRemoval = str(invoice.waste_removal),
        # amountDue = str(invoice.amount_due),
        # tax = str(invoice.tax),
        # total = str(invoice.total),
        # deposit = str(invoice.deposit),
        # paymentAmount = str(invoice.payment_amount),
        # paymentDate = invoice.payment_date.strftime('%B %d, %Y'),
        # cash = "X" if invoice.is_cash else "",
        # cheque = "X" if invoice.is_cheque else "",
        # debit = "X" if invoice.is_debit else "",
        # credit = "X" if invoice.is_credit else "",
        # other = "X" if invoice.is_other else "",
        # clientSignature = str(invoice.client_signature),
        # associateSignDate = invoice.associate_sign_date.strftime('%B %d, %Y'),
        # associateSignature = str(invoice.associate_signature),
        # workOrderId = str(invoice.work_order_id),

        with grpc.insecure_channel(settings.WORKERY_INVOICEBUILDER_MICROSERVICE_ADDRESS_AND_PORT) as channel:
            stub = invoice_pb2_grpc.InvoiceBuilderStub(channel)
            response = stub.GeneratePDF(invoice_pb2.GeneratePDFRequest(
                invoiceId=str(invoice.invoice_id),
                invoiceDate=invoice.invoice_date.strftime('%B %d, %Y'),
                associateName=str(invoice.associate_name),
                associateTelephone = str(invoice.associate_telephone),
                clientName = str(invoice.client_name),
                clientAddress = str(invoice.client_address),
                clientTelephone = str(invoice.client_telephone),
                clientEmail = str(invoice.client_email),
                line01Quantity = str(invoice.line_01_qty),
                line01Description = str(invoice.line_01_desc),
                line01Price = str(invoice.line_01_price),
                line01Amount = str(invoice.line_01_amount),
                line02Quantity =  str(invoice.line_02_qty) if invoice.line_02_qty else "",
                line02Description = str(invoice.line_02_desc) if invoice.line_02_qty else "",
                line02Price = str(invoice.line_02_price) if invoice.line_02_qty else "",
                line02Amount = str(invoice.line_02_amount) if invoice.line_02_qty else "",
                line03Quantity = str(invoice.line_03_qty) if invoice.line_03_qty else "",
                line03Description = str(invoice.line_03_desc) if invoice.line_03_qty else "",
                line03Price = str(invoice.line_03_price) if invoice.line_03_qty else "",
                line03Amount = str(invoice.line_03_amount) if invoice.line_03_qty else "",
                line04Quantity = str(invoice.line_04_qty) if invoice.line_04_qty else "",
                line04Description = str(invoice.line_04_desc) if invoice.line_04_qty else "",
                line04Price = str(invoice.line_04_price) if invoice.line_04_qty else "",
                line04Amount = str(invoice.line_04_amount) if invoice.line_04_qty else "",
                line05Quantity = str(invoice.line_05_qty) if invoice.line_05_qty else "",
                line05Description = str(invoice.line_05_desc) if invoice.line_05_qty else "",
                line05Price = str(invoice.line_05_price) if invoice.line_05_qty else "",
                line05Amount = str(invoice.line_05_amount) if invoice.line_05_qty else "",
                line06Quantity = str(invoice.line_06_qty) if invoice.line_06_qty else "",
                line06Description = str(invoice.line_06_desc) if invoice.line_06_qty else "",
                line06Price = str(invoice.line_06_price) if invoice.line_06_qty else "",
                line06Amount = str(invoice.line_06_amount) if invoice.line_06_qty else "",
                line07Quantity = str(invoice.line_07_qty) if invoice.line_07_qty else "",
                line07Description = str(invoice.line_07_desc) if invoice.line_07_qty else "",
                line07Price = str(invoice.line_07_price) if invoice.line_07_qty else "",
                line07Amount = str(invoice.line_07_amount) if invoice.line_07_qty else "",
                line08Quantity = str(invoice.line_08_qty) if invoice.line_08_qty else "",
                line08Description = str(invoice.line_08_desc) if invoice.line_08_qty else "",
                line08Price = str(invoice.line_08_price) if invoice.line_08_qty else "",
                line08Amount = str(invoice.line_08_amount) if invoice.line_08_qty else "",
                line09Quantity = str(invoice.line_09_qty) if invoice.line_09_qty else "",
                line09Description = str(invoice.line_09_desc) if invoice.line_09_qty else "",
                line09Price = str(invoice.line_09_price) if invoice.line_09_qty else "",
                line09Amount = str(invoice.line_09_amount) if invoice.line_09_qty else "",
                line10Quantity = str(invoice.line_10_qty) if invoice.line_10_qty else "",
                line10Description = str(invoice.line_10_desc) if invoice.line_10_qty else "",
                line10Price = str(invoice.line_10_price) if invoice.line_10_qty else "",
                line10Amount = str(invoice.line_10_amount) if invoice.line_10_qty else "",
                line11Quantity = str(invoice.line_11_qty) if invoice.line_11_qty else "",
                line11Description = str(invoice.line_11_desc) if invoice.line_11_qty else "",
                line11Price = str(invoice.line_11_price) if invoice.line_11_qty else "",
                line11Amount = str(invoice.line_11_amount) if invoice.line_11_qty else "",
                line12Quantity = str(invoice.line_12_qty) if invoice.line_12_qty else "",
                line12Description = str(invoice.line_12_desc) if invoice.line_12_qty else "",
                line12Price = str(invoice.line_12_price) if invoice.line_12_qty else "",
                line12Amount = str(invoice.line_12_amount) if invoice.line_12_qty else "",
                line13Quantity = str(invoice.line_13_qty) if invoice.line_13_qty else "",
                line13Description = str(invoice.line_13_desc) if invoice.line_13_qty else "",
                line13Price = str(invoice.line_13_price) if invoice.line_13_qty else "",
                line13Amount = str(invoice.line_13_amount) if invoice.line_13_qty else "",
                line14Quantity = str(invoice.line_14_qty) if invoice.line_14_qty else "",
                line14Description = str(invoice.line_14_desc) if invoice.line_14_qty else "",
                line14Price = str(invoice.line_14_price) if invoice.line_14_qty else "",
                line14Amount = str(invoice.line_14_amount) if invoice.line_14_qty else "",
                line15Quantity = str(invoice.line_15_qty) if invoice.line_15_qty else "",
                line15Description = str(invoice.line_15_desc) if invoice.line_15_qty else "",
                line15Price = str(invoice.line_15_price) if invoice.line_15_qty else "",
                line15Amount = str(invoice.line_15_amount) if invoice.line_15_qty else "",
                invoiceQuoteDays = str(invoice.invoice_quote_days),
                invoiceAssociateTax = str(invoice.invoice_associate_tax),
                invoiceQuoteDate = invoice.invoice_quote_date.strftime('%B %d, %Y'),
                invoiceCustomersApproval = str(invoice.invoice_customers_approval),
                line01Notes = str(invoice.line_01_notes),
                line02Notes = str(invoice.line_02_notes) if invoice.line_02_notes else "",
                totalLabour = str(invoice.total_labour),
                totalMaterials = str(invoice.total_materials),
                wasteRemoval = str(invoice.waste_removal),
                amountDue = str(invoice.amount_due),
                tax = str(invoice.tax),
                total = str(invoice.total),
                deposit = str(invoice.deposit),
                paymentAmount = str(invoice.payment_amount),
                paymentDate = invoice.payment_date.strftime('%B %d, %Y'),
                cash = "X" if invoice.is_cash else "",
                cheque = "X" if invoice.is_cheque else "",
                debit = "X" if invoice.is_debit else "",
                credit = "X" if invoice.is_credit else "",
                other = "X" if invoice.is_other else "",
                clientSignature = str(invoice.client_signature),
                associateSignDate = invoice.associate_sign_date.strftime('%B %d, %Y'),
                associateSignature = str(invoice.associate_signature),
                workOrderId = str(invoice.work_order_id),
            ))

            # Generate the filename.
            work_order_id = str(invoice.work_order_id)
            invoice_id = str(invoice.invoice_id)
            pdf_filename = work_order_id+"-"+invoice_id+".pdf"

            # Save the data from the gRPC.
            save_chunks_to_file(response, "media/"+pdf_filename)

            # Open the file.
            with open('media/'+pdf_filename, 'rb') as report:
                return Response(
                    report.read(),
                    headers={'Content-Disposition': 'attachment; filename="'+pdf_filename+'"'},
                    content_type='application/pdf'
                )