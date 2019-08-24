# -*- coding: utf-8 -*-
import phonenumbers
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

from shared_foundation.custom.drf.fields import PhoneNumberField
from tenant_foundation.models import ActivitySheetItem


class ActivitySheetItemListCreateSerializer(serializers.ModelSerializer):
    # text = serializers.CharField(
    #     required=True,
    #     allow_blank=False,
    #     allow_null=False,
    #     validators=[]
    # )
    associate_full_name = serializers.SerializerMethodField()
    associate_telephone = PhoneNumberField(read_only=True, source="associate.telephone")
    associate_e164_telephone = serializers.SerializerMethodField()
    associate_email = serializers.EmailField(read_only=True, source="associate.email")
    pretty_state = serializers.CharField(read_only=True, source="get_pretty_state")

    class Meta:
        model = ActivitySheetItem
        fields = (
            'id',
            'job',
            'ongoing_job',
            'associate',
            'associate_full_name',
            'associate_telephone',
            'associate_e164_telephone',
            'associate_email',
            'comment',
            'state',
            'pretty_state',
            'created_at',
            'created_by',
        )

    def get_associate_full_name(self, obj):
        try:
            if obj.associate:
                return str(obj.associate)
        except Exception as e:
            pass
        return None

    def get_associate_e164_telephone(self, obj):
        """
        Converts the "PhoneNumber" object into a "NATIONAL" format.
        See: https://github.com/daviddrysdale/python-phonenumbers
        """
        try:
            if obj.associate.telephone:
                return phonenumbers.format_number(obj.associate.telephone, phonenumbers.PhoneNumberFormat.E164)
            else:
                return "-"
        except Exception as e:
            print(e)
            return None



class ActivitySheetItemRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        validators=[]
    )
    class Meta:
        model = ActivitySheetItem
        fields = (
            'id',
            'job',
            'ongoing_job',
            'associate',
            'comment',
            'state',
            'created_at',
            'created_by',
        )
