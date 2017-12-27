# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from shared_foundation.models.me import SharedMe
from shared_foundation import utils


class AuthCustomTokenSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username', None)
        password = attrs.get('password', None)

        try:
            user = User.objects.get(
                Q(email=email_or_username) |
                Q(username=email_or_username)
            )
        except User.DoesNotExist:
            raise exceptions.ValidationError(_('Password or email is not valid.'))

        if not user.is_active:
            raise exceptions.ValidationError(_('Your account is suspended!'))

        authenticated_user = authenticate(username=email_or_username, password=password)

        if authenticated_user:
            attrs['authenticated_user'] = authenticated_user
            return attrs
        else:
            raise exceptions.ValidationError(_('Password or email is not valid.'))
