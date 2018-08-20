# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework import generics
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.response import Response
from shared_foundation.models.franchise import SharedFranchise
from shared_api.serializers.franchise_serializers import SharedFranchiseListCreateSerializer
from shared_api.custom_pagination import TinyResultsSetPagination


class SharedFranchiseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SharedFranchiseListCreateSerializer
    pagination_class = TinyResultsSetPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        """
        Overriding the initial queryset
        """
        queryset = SharedFranchise.objects.all().exclude(schema_name="public").order_by('name')

        # Set up eager loading to avoid N+1 selects
        s = self.get_serializer_class()
        queryset = s.setup_eager_loading(self, queryset)
        return queryset

    # def post(self, request, format=None):
    #     """
    #     Create
    #     """
    #     serializer = AssociateListCreateSerializer(data=request.data, context={
    #         'created_by': request.user
    #     })
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)



class SharedFranchiseCreateValidationAPIView(generics.CreateAPIView):
    """
    API endpoint strictly used for POST creation validations of the
    `SharedFranchise` model before an actual POST create API call is made.
    """
    serializer_class = SharedFranchiseListCreateSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    def post(self, request, format=None):
        """
        Create
        """
        serializer = SharedFranchiseListCreateSerializer(data=request.data, context={
            'created_by': request.user,
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
