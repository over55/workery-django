# -*- coding: utf-8 -*-
import django_filters
import django_rq
from django.conf.urls import url, include
from django.core.management import call_command
from django_filters import rest_framework as filters
from django.db.models import Q
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins # See: http://www.django-rest-framework.org/api-guide/generic-views/#mixins
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.decorators import detail_route, list_route # See: http://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
from rest_framework.response import Response
from shared_foundation import models
from shared_api.serializers.auth_register_customer_serializers import RegisterCustomerSerializer


class RegisterCustomerAPIView(APIView):
    """
    Create a user instance.
    """
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        """
        Create the user & email user with an activation email.
        """
        # Load up the data into the serializer & validate it.
        serializer = RegisterCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the models.
        serializer.save()

        # Return status true that we successfully registered the user.
        return Response(serializer.data, status=status.HTTP_201_CREATED)
