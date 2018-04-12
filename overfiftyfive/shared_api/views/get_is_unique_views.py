# -*- coding: utf-8 -*-
from django.db.models import Q
from django.db import connection # Used for django tenants.
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from shared_foundation.models import SharedUser


class GetIsUniqueAPIView(APIView):
    """
    API-endpoint used for looking up an email address to check if is unique.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        connection.set_schema_to_public() # Switch to Public.

        email = self.request.POST.get('email', '').lower()
        found_email = SharedUser.objects.filter(email__iexact=email).exists()

        return Response(
            data=0 if found_email else 1,
            status=status.HTTP_200_OK
        )
