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
            'reason_other',
            'until_further_notice',
            'until_date',
        )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------
        # Get our inputs.
        #-----------------------------
        associate = validated_data.get('associate', None)
        reason = validated_data.get('reason', None)
        until_further_notice = validated_data.get('until_further_notice', False)
        until_date = validated_data.get('until_date', None)

        #-----------------------------
        # Create our `AwayLog` object.
        #-----------------------------
        # Create our log.
        log = AwayLog.objects.create(
            associate=associate,
            reason=reason,
            until_further_notice=until_further_notice,
            until_date=until_date,
            created_by=self.context['created_by'],
            last_modified_by=self.context['created_by'],
        )

        # Save our away information to the associate.
        associate.away_log = log
        associate.save()

        # Return our validated data.
        validated_data['id'] = log.id
        return validated_data


class AwayLogRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    class Meta:
        model = AwayLog
        fields = (
            'id',
            'associate',
            'reason',
            'reason_other',
            'until_further_notice',
            'until_date',
        )
