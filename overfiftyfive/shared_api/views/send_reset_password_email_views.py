# -*- coding: utf-8 -*-
import django_filters
import django_rq
from django.conf.urls import url, include
from django.core.management import call_command
from django_filters import rest_framework as filters
from django.db.models import Q
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import authentication, viewsets, permissions, status
from rest_framework.decorators import detail_route, list_route # See: http://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
from rest_framework.response import Response
from shared_foundation import models
from shared_api.serializers.send_password_reset_serializers import SendResetPasswordEmailSerializer


class SendResetPasswordEmailAPIView(APIView):
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = SendResetPasswordEmailSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            call_command('send_reset_password_email', serializer.validated_data['email_or_username'], verbosity=0)

            # Return status true that we successfully registered the user.
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
