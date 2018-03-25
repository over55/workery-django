import django_filters
from django.conf.urls import url, include
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.db import connection # Used for django tenants.
from django_filters import rest_framework as filters
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework import mixins # See: http://www.django-rest-framework.org/api-guide/generic-views/#mixins
from rest_framework import authentication, viewsets, permissions, status, parsers, renderers
from rest_framework.decorators import detail_route, list_route # See: http://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
from rest_framework.response import Response
from shared_foundation.models import SharedFranchise, SharedUser
from shared_api.serializers.auth_login_serializers import AuthCustomTokenSerializer


class LoginAPIView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        """
        # Source: https://stackoverflow.com/a/28218467
        """
        # Connection needs first to be at the public schema, as this is where
        # the database needs to be set before creating a new tenant. If this is
        # not done then django-tenants will raise a "Can't create tenant outside
        # the public schema." error.
        connection.set_schema_to_public() # Switch to Public.

        # Serializer to get our login details.
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        authenticated_user = serializer.validated_data['authenticated_user']

        print(authenticated_user.franchise)

        # Authenticate with the public.
        login(self.request, authenticated_user)

        token, created = Token.objects.get_or_create(user=authenticated_user)

        # SAVE ALL THE USER PROFILE INFORMATION TO A SESSION.
        request.session['me_token_key'] = str(token.key)
        request.session['me_schema_name'] = str(authenticated_user.franchise.schema_name)
        request.session['me_user_id'] = str(authenticated_user.id)

        # # Connection will set it back to our tenant.
        connection.set_schema(authenticated_user.franchise.schema_name, True) # Switch to Tenant.

        # Authenticate with the tenant.
        login(self.request, authenticated_user)

        # Return the user session information.
        return Response(
            data = {
                'token': str(token.key),
                'schema_name': authenticated_user.franchise.schema_name,
                'email': str(authenticated_user),
            },
            status=status.HTTP_200_OK
        )
