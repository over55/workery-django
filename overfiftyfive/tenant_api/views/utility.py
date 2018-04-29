# -*- coding: utf-8 -*-
from django.db.models import Q
from django.db import connection # Used for django tenants.
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from tenant_foundation.models import Customer, Organization
from tenant_api.serializers.customer import CustomerRetrieveUpdateDestroySerializer


class FindCustomerMatchingAPIView(APIView):
    """
    API-endpoint used for looking up an organization name to check if is unique.
    """
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request):
        # Get our extracts.
        customer = None
        email = self.request.GET.get('email', None)
        company_name = self.request.GET.get('organization_name', None)

        if company_name is not '' and email is not '':
            print("Searching: company_name and email")
            customer = Customer.objects.filter(
                email__iexact=email,
                organization__name__iexact=company_name
            ).first()

        elif email is '' and company_name is not '':
            print("Searching: company_name")
            customer = Customer.objects.filter(
                organization__name__iexact=company_name
            ).first()

        elif email is not '' and company_name is '':
            print("Searching: email")
            customer = Customer.objects.filter(
                email__iexact=email,
            ).first()

        print("Found", customer)

        if customer:
            serializer = CustomerRetrieveUpdateDestroySerializer(customer, many=False)
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )

        else:
            # Return our results.
            return Response(
                data={},
                status=status.HTTP_200_OK
            )
