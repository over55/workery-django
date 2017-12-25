# -*- coding: utf-8 -*-
import django_filters
import django_rq
from django.core.management import call_command
from django.db.models import Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from shared_api.serializers.auth_reset_password_serializers import ResetPasswordSerializer
from shared_foundation.models import SharedMe


class ResetPasswordAPIView(APIView):
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = serializer.validated_data['password']
            pr_access_code = serializer.validated_data['pr_access_code']

            # Update the password if it exists.
            try:
                me = SharedMe.objects.get(pr_access_code=pr_access_code)
                me.user.set_password(password)
                me.user.save()

                # Security: Remove the "pr_access_code" so it cannot be used again.
                me.pr_access_code = ''
                me.save()

                # Return status true that we successfully reset password for the user.
                return Response(None, status=status.HTTP_200_OK)
            except SharedMe.DoesNotExist:
                # Return an error based on a D.N.E.
                return Response(
                    _("Password reset access code does not exist."),
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Return error.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
