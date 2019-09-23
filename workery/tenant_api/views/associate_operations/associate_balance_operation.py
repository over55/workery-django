# -*- coding: utf-8 -*-
from ipware import get_client_ip
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.conf.urls import url, include
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response

from shared_foundation.custom.drf.permissions import IsAuthenticatedAndIsActivePermission
from tenant_foundation.models import Associate
from tenant_api.pagination import TinyResultsSetPagination
from tenant_api.permissions.order import (
   CanListCreateWorkOrderPermission,
   CanRetrieveUpdateDestroyWorkOrderPermission
)
from tenant_api.serializers.associate_operations.associate_balance_operation import AssociateBalanceOperationSerializer


class AssociateBalanceOperationAPIView(generics.RetrieveAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsAuthenticatedAndIsActivePermission,
        CanRetrieveUpdateDestroyWorkOrderPermission
    )

    @transaction.atomic
    def get(self, request):
        """
        Retrieve
        """
        associate_id = self.request.query_params.get('id', None)
        if associate_id is None:
            return Response(
                data=[{'id': 'missingin'}],
                status=status.HTTP_400_BAD_REQUEST
            )
        associate_id = int(associate_id)

        associate = get_object_or_404(Associate, pk=associate_id)

        self.check_object_permissions(request, associate)  # Validate permissions.
        serializer = AssociateBalanceOperationSerializer(associate, many=False)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )
