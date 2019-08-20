# -*- coding: utf-8 -*-
import logging
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
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField
from shared_foundation.constants import ASSOCIATE_GROUP_ID, FRONTLINE_GROUP_ID
from shared_foundation.custom.drf.validation import MatchingDuelFieldsValidator, EnhancedPasswordStrengthFieldValidator
from shared_foundation.utils import (
    get_unique_username_from_email,
    int_or_none
)
from shared_foundation.models import SharedUser
from tenant_foundation.models import (
    Comment,
    StaffComment,
    Staff,
    HowHearAboutUsItem
)
from tenant_api.serializers.tag import TagListCreateSerializer


logger = logging.getLogger(__name__)


class StaffMetricsUpdateSerializer(serializers.ModelSerializer):
    # Attach with our foreign keys.
    how_hear = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        allow_null=False,
        queryset=HowHearAboutUsItem.objects.all()
    )

    # Meta Information.
    class Meta:
        model = Staff
        fields = (
            'tags',
            'gender',
            'birthdate',
            'how_hear',
            'how_hear_other',
            'join_date',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'owner',
            'created_by',
            'last_modified_by',
            # 'comments'
            'tags',
        )
        return queryset

    def update(self, instance, validated_data):
        """
        Override this function to include extra functionality.
        """
        # For debugging purposes only.
        # print(validated_data)

        # Get our inputs.
        email = instance.email

        #-------------------------------------
        # Bugfix: Created `SharedUser` object.
        #-------------------------------------
        if instance.owner is None:
            owner = SharedUser.objects.filter(email=email).first()
            if owner:
                instance.owner = owner
                instance.save()
                logger.info("BUGFIX: Attached existing shared user to staff.")
            else:
                instance.owner = SharedUser.objects.create(
                    first_name=instance.given_name,
                    last_name=instance.last_name,
                    email=email,
                    is_active=True,
                    franchise=self.context['franchise'],
                    was_email_activated=True
                )
                instance.save()
                logger.info("BUGFIX: Created shared user and attached to staff.")

        #---------------------------
        # Update `Staff` object.
        #---------------------------
        # Person
        instance.birthdate=validated_data.get('birthdate', None)
        instance.join_date=validated_data.get('join_date', None)
        instance.gender=validated_data.get('gender', None)
        instance.how_hear=validated_data.get('how_hear', None)
        instance.how_hear_other=validated_data.get('how_hear_other', None)

        instance.last_modified_by = self.context['last_modified_by']
        instance.last_modified_from = self.context['last_modified_from']
        instance.last_modified_from_is_public = self.context['last_modified_from_is_public']

        # Save our instance.
        instance.save()
        logger.info("Updated the staff member.")

        #------------------------
        # Set our `Tag` objects.
        #------------------------
        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                instance.tags.set(tags)

        # #---------------------------
        # # Attach our comment.
        # #---------------------------
        # extra_comment = validated_data.get('extra_comment', None)
        # if extra_comment is not None:
        #     comment = Comment.objects.create(
        #         created_by=self.context['last_modified_by'],
        #         last_modified_by=self.context['last_modified_by'],
        #         text=extra_comment,
        #         created_from = self.context['last_modified_from'],
        #         created_from_is_public = self.context['last_modified_from_is_public']
        #     )
        #     staff_comment = StaffComment.objects.create(
        #         staff=instance,
        #         comment=comment,
        #     )
        #
        # #---------------------------
        # # Update validation data.
        # #---------------------------
        # # validated_data['comments'] = StaffComment.objects.filter(staff=instance)
        # validated_data['last_modified_by'] = self.context['last_modified_by']
        # # validated_data['extra_comment'] = None

        # Return our validated data.
        return instance
