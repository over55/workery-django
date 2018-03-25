# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status
from rest_framework.response import Response
from shared_foundation.models import SharedUser


class GetIsUniqueAPIView(APIView):
    """
    API-endpoint used for looking up an email address to check if is unique.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        email = self.request.query_params.get('email', '').lower()
        is_email_unique = SharedUser.objects.filter(email=email).exists()
        return Response(
            data=1 if is_email_unique else 0,
            status=status.HTTP_200_OK
        )
