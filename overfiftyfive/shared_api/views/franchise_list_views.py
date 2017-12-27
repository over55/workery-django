# -*- coding: utf-8 -*-
import django_filters
from django_filters import rest_framework as filters
from django.conf.urls import url, include
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from shared_foundation.models.franchise import SharedFranchise
from shared_api.serializers.franchise_serializers import SharedFranchiseListSerializer
from shared_api.custom_pagination import TinyResultsSetPagination
from shared_api.filters.franchise_filters import SharedFranchiseListFilter


class SharedFranchiseListAPIView(generics.ListAPIView):
    serializer_class = SharedFranchiseListSerializer
    pagination_class = TinyResultsSetPagination
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_class = SharedFranchiseListFilter

    def get_queryset(self):
        """
        Overriding the initial queryset
        """
        queryset = SharedFranchise.objects.all().exclude(schema_name="public").order_by('name')

        # Set up eager loading to avoid N+1 selects
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)
        return queryset
