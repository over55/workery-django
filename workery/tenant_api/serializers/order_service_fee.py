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

from tenant_foundation.models import WorkOrderServiceFee


class WorkOrderServiceFeeListCreateSerializer(serializers.ModelSerializer):
    is_archived = serializers.BooleanField(read_only=True)
    title = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        validators=[]
    )
    class Meta:
        model = WorkOrderServiceFee
        fields = (
            'id',
            'title',
            'percentage',
            'description',
            'is_archived'
        )



class WorkOrderServiceFeeRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    is_archived = serializers.BooleanField(read_only=True)
    title = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        validators=[]
    )
    class Meta:
        model = WorkOrderServiceFee
        fields = (
            'id',
            'title',
            'percentage',
            'description',
            'is_archived'
        )
