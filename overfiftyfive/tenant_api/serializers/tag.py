# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from tenant_foundation.models import Tag


class TagListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'text'
        )



class TagRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            # Thing
            'text',
        )
