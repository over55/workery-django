# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from tenant_foundation.models import AwayLog


class AwayLogListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AwayLog
        fields = (
            'id',
            'associate',
            'reason',
            'until_further_notice',
            'until_date',
            'created',
            'created_by',
            'last_modified',
            'last_modified_by'
        )



class AwayLogRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    class Meta:
        model = AwayLog
        fields = (
            'id',
            'associate',
            'reason',
            'until_further_notice',
            'until_date',
            'created',
            'created_by',
            'last_modified',
            'last_modified_by'
        )
