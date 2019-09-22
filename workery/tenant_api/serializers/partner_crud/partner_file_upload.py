# -*- coding: utf-8 -*-
import phonenumbers
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
from rest_framework.validators import UniqueValidator

from shared_foundation.custom.drf.fields import PhoneNumberField, GenericFileBase64File
from shared_foundation.constants import CUSTOMER_GROUP_ID
from shared_foundation.models import SharedUser
from shared_foundation.utils import get_content_file_from_base64_string
# from tenant_api.serializers.partner_comment import PartnerCommentSerializer
from tenant_foundation.constants import *
from tenant_foundation.models import (
    Partner,
    PrivateFileUpload,
    Tag
)


class PartnerFileUploadListCreateSerializer(serializers.ModelSerializer):
    partner = serializers.PrimaryKeyRelatedField(many=False, queryset=Partner.objects.all(), required=True,)
    file_url = serializers.FileField(
        read_only=True,
        max_length=None,
        use_url=True,
        source="data_file"
    )
    title = serializers.CharField(required=True, allow_null=False,)
    description = serializers.CharField(required=True, allow_null=False,)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), allow_null=True)
    is_archived = serializers.BooleanField(required=True,)
    created_at = serializers.DateTimeField(read_only=True, allow_null=False,)

    # REACT-DJANGO UPLOAD | STEP 1 OF 4: We define two string fields required (write-only)
    # for accepting our file uploads.
    upload_content = serializers.CharField(write_only=True, allow_null=False,)
    upload_filename = serializers.CharField(write_only=True, allow_null=False,)

    # Meta Information.
    class Meta:
        model = PrivateFileUpload
        fields = (
            'id',
            'partner',
            'file_url',
            'title',
            'description',
            'tags',
            'is_archived',
            'created_at',

            # REACT-DJANGO UPLOAD | STEP 2 OF 4: Define required fields.
            'upload_content',
            'upload_filename',
        )

    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(
            'partner',
        )
        return queryset

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """

        # Extract our upload file data
        content = validated_data.get('upload_content')
        filename = validated_data.get('upload_filename')
        if settings.DEBUG:
            filename = "QA_"+filename # NOTE: Attach `QA_` prefix if server running in QA mode.
        content_file = get_content_file_from_base64_string(content, filename) # REACT-DJANGO UPLOAD | STEP 3 OF 4: Convert to `ContentFile` type.

        # Create our file.
        private_file = PrivateFileUpload.objects.create(
            title = validated_data.get('title'),
            description = validated_data.get('description'),
            is_archived = validated_data.get('is_archived'),
            partner = validated_data.get('partner'),
            data_file = content_file, # REACT-DJANGO UPLOAD | STEP 4 OF 4: When you attack a `ContentFile`, Django handles all file uploading.
            created_by = self.context['created_by'],
            created_from = self.context['created_from'],
            created_from_is_public = self.context['created_from_is_public'],
            last_modified_by = self.context['created_by'],
            last_modified_from = self.context['created_from'],
            last_modified_from_is_public = self.context['created_from_is_public'],
        )

        tags = validated_data.get('tags', None)
        if tags is not None:
            if len(tags) > 0:
                private_file.tags.set(tags)

        # For debugging purposes only.
        print("Created private file #", private_file)

        # Return our validated data.
        return private_file
