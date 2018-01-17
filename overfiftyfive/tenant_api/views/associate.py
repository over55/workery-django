# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from tenant_api.pagination import StandardResultsSetPagination
from tenant_api.serializers.associate import (
    AssociateListCreateSerializer,
    AssociateRetrieveUpdateDestroySerializer
)
from tenant_foundation.models import Associate


class AssociateListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssociateListCreateSerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        queryset = Associate.objects.all()
        #TODO: IMPLEMENT.
        return queryset

    def post(self, request, format=None):
        #TODO: IMPLEMENT.
        return Response(data=[], status=status.HTTP_201_CREATED)


class AssociateRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssociateRetrieveUpdateDestroySerializer
    pagination_class = StandardResultsSetPagination
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request, pk=None):
        #TODO: IMPLEMENT.
        return Response(
            data=[],
            status=status.HTTP_200_OK
        )

    def put(self, request, pk=None):
        #TODO: IMPLEMENT.
        return Response(data=[], status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        #TODO: IMPLEMENT.
        return Response(data=[], status=status.HTTP_200_OK)
