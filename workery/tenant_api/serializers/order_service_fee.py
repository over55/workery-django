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
from tenant_foundation.models import OrderServiceFee


class OrderServiceFeeListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderServiceFee
        fields = (
            'id',
            'title',
            'percentage',
            'description'
        )



class OrderServiceFeeRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderServiceFee
        fields = (
            'id',
            'title',
            'percentage',
            'description',
        )
