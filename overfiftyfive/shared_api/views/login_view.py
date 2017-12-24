import django_filters
from django.conf.urls import url, include
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django_filters import rest_framework as filters
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework import mixins # See: http://www.django-rest-framework.org/api-guide/generic-views/#mixins
from rest_framework import authentication, viewsets, permissions, status, parsers, renderers
from rest_framework.decorators import detail_route, list_route # See: http://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
from rest_framework.response import Response
from shared_foundation.models.me import SharedMe
from shared_api.serializers.login_serializers import AuthCustomTokenSerializer


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
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        authenticated_user = serializer.validated_data['authenticated_user']

        login(self.request, authenticated_user)

        token, created = Token.objects.get_or_create(user=authenticated_user)

        me = SharedMe.objects.get(user=authenticated_user)

        return Response(
            data = {
                'token': str(token.key),
                'me': str(me)
            },
            status=status.HTTP_200_OK
        )
