# -*- coding: utf-8 -*-
import django_filters
import django_rq
from django.core.management import call_command
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.authtoken.models import Token
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

        # Perform validation.
        serializer.is_valid(raise_exception=True)

        # Get our validated variables.
        password = serializer.validated_data['password']
        me = serializer.validated_data['me']

        # Update the password.
        me.user.set_password(password)
        me.user.save()

        # Security: Remove the "pr_access_code" so it cannot be used again.
        me.pr_access_code = ''
        me.save()

        # DEVELOPER NOTES:
        # - The code below is similar to the "sign-in" API endpoint.
        # - We are essentially authenticating the user and creating a
        #   session for the authenticated user.
        # - We will get our API token and return it.
        # - We will return our profile info.

        # Authenticate with the tenant.
        authenticated_user = authenticate(username=me.user.username, password=password)
        login(self.request, authenticated_user)

        token, created = Token.objects.get_or_create(user=authenticated_user)

        # Return status true that we successfully reset password for the user.
        # Return the user session information.
        return Response(
            data = {
                'token': str(token.key),
                'schema_name': None if me.franchise is None else me.franchise.schema_name,
                'email': str(me),
            },
            status=status.HTTP_200_OK
        )
