# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response

from tenant_foundation.models import (
    AwayLog,
    Associate,
    AssociateComment,
    Comment
)


logger = logging.getLogger(__name__)


class AwayLogListCreateSerializer(serializers.ModelSerializer):

    until_further_notice = serializers.BooleanField(
        write_only=True,
        required=True,
        error_messages={
            "invalid": "Please pick either 'Yes' or 'No' choice."
        }
    )

    class Meta:
        model = AwayLog
        fields = (
            'id',
            'associate',
            'reason',
            'reason_other',
            'until_further_notice',
            'until_date',
            'start_date',
        )

    def validate_reason(self, value):
        if value is None or value == "null" or value == "0" or value == 0:
            raise serializers.ValidationError("Please pick a reason.")
        return value

    def validate_associate(self, value):
        """
        Include validation so no existing AWayLog objects exist which where
        not deleted.
        """
        if value:
            has_existing_log = AwayLog.objects.filter(
                associate=value,
                was_deleted=False
            ).exists()
            if has_existing_log:
                raise serializers.ValidationError("Cannot create a new log entry, you must delete the previous log entry before creating a new one!")
        return value

    def validate(self, data):
        """
        Override the validator to provide additional custom validation based
        on our custom logic.
        """
        # CASE 1 - Other reason
        if data['reason'] == 1 or data['reason'] == "1":
            reason_other = data['reason_other']
            if reason_other == "":
                raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))

        # CASE 2 - No `until_date` chosen when `until_further_notice` is "no" selected.
        if data['until_further_notice'] is False:
            if data['until_date'] is None:
                raise serializers.ValidationError("Please provide a date for \"until date\".")
        return data  # Return our data.

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------
        # Get our inputs.
        #-----------------------------
        associate = validated_data.get('associate', None)
        reason = validated_data.get('reason', None)
        reason_other = validated_data.get('reason_other', None)
        until_further_notice = validated_data.get('until_further_notice', False)
        until_date = validated_data.get('until_date', None)
        start_date = validated_data.get('start_date', None)

        #-----------------------------
        # Create our `AwayLog` object.
        #-----------------------------
        # Create our log.
        log = AwayLog.objects.create(
            associate=associate,
            reason=reason,
            reason_other=reason_other,
            until_further_notice=until_further_notice,
            until_date=until_date,
            start_date=start_date,
            created_by=self.context['created_by'],
            # created_from = self.context['created_from'],
            # created_from_is_public = self.context['created_from_is_public'],
            last_modified_by=self.context['created_by'],
            # last_modified_from=self.context['created_from'],
            # last_modified_from_is_public=self.context['created_from_is_public'],
        )
        logger.info("Created AwayLog")

        # Save our away information to the associate.
        associate.away_log = log
        associate.save()
        logger.info("Assigned AwayLog to associate.")

        #-----------------------------
        # Create our `Comment` object.
        #-----------------------------
        # Create our comment text.
        utc_dt = timezone.now()
        current_dt = self.context['franchise'].to_tenant_dt(utc_dt)
        user = self.context['created_by']
        comment_text = "System Note: Staff member ID #" + str(user.id)
        comment_text += " has set the Associate to away on " +  str(current_dt) + ". "
        comment_text += "The away reason is: "
        if log.reason == 1:
            comment_text += str(log.reason_other)
        elif log.reason == 2:
            comment_text += "Going on vacation"
        elif log.reason == 3:
            comment_text += "Personal reasons"
        elif log.reason == 4:
            comment_text += "Insurance expired"
        elif log.reason == 5:
            comment_text += "Policy check expired"
        if log.until_further_notice == False:
            comment_text += ". Until: "+str(log.until_date)
        else:
            comment_text += ". Until: Further notice."

        # Create our object.
        comment_obj = Comment.objects.create(
            created_by = user,
            last_modified_by = user,
            text=comment_text,
            # created_from = self.context['created_from'],
            # created_from_is_public = self.context['created_from_is_public']
        )
        associate_comment = AssociateComment.objects.create(
            about=associate,
            comment=comment_obj,
        )

        # For debugging purposes only.
        logger.info("Associate comment created.")

        #-----------------------------
        # Return our validated result.
        #-----------------------------
        # Return our validated data.
        validated_data['id'] = log.id
        return validated_data


class AwayLogRetrieveUpdateDestroySerializer(serializers.ModelSerializer):

    until_further_notice = serializers.BooleanField(
        write_only=True,
        required=True,
        error_messages={
            "invalid": "Please pick either 'Yes' or 'No' choice."
        }
    )

    class Meta:
        model = AwayLog
        fields = (
            'id',
            'associate',
            'reason',
            'reason_other',
            'until_further_notice',
            'until_date',
            'start_date',
        )

    def validate_reason(self, value):
        if value is None or value == "null" or value == "0" or value == 0:
            raise serializers.ValidationError("Please pick a reason.")
        return value

    def validate(self, data):
        """
        Override the validator to provide additional custom validation based
        on our custom logic.
        """
        # CASE 1 - Other reason
        if data['reason'] == 1 or data['reason'] == "1":
            reason_other = data['reason_other']
            if reason_other == "":
                raise serializers.ValidationError(_("Please provide a reason as to why you chose the \"Other\" option."))

        # CASE 2 - No `until_date` chosen when `until_further_notice` is "no" selected.
        if data['until_further_notice'] is False:
            if data['until_date'] is None:
                raise serializers.ValidationError("Please provide a date for \"until date\".")
        return data  # Return our data.
