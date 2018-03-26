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
# from tenant_api.serializers.comment import CommentListCreateSerializer
from tenant_foundation.models import CustomerAffiliation


class CustomerAffiliationSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    # organization = CommentListCreateSerializer(many=False, read_only=True)

    class Meta:
        model = CustomerAffiliation
        fields = (
            'customer',
            'organization',
            'type_of',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'customer',
            'organization',
        )
        return queryset
