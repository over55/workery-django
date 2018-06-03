# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from starterkit.utils import (
    int_or_none
)
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db.models import Q, Prefetch
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from shared_api.custom_fields import Base64ImageField
from tenant_foundation.models import (
    Associate,
    Customer,
    Partner,
    PublicImageUpload,
    Staff
)


logger = logging.getLogger(__name__)


class PublicImageUploadListCreateSerializer(serializers.ModelSerializer):

    image_file = Base64ImageField(
        max_length=None,
        use_url=True,
        write_only=True,
    )
    upload_type_of = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True
    )
    upload_id = serializers.CharField(
        required=True,
        write_only=True
    )

    class Meta:
        model = PublicImageUpload
        fields = (
            'id',
            'image_file',
            'upload_type_of',
            'upload_id'
        )

    def create(self, validated_data):
        """
        Override the `create` function to add extra functinality.
        """
        #-----------------------------
        # Get our inputs.
        #-----------------------------
        image_file = validated_data.get('image_file', None)
        upload_type_of = validated_data.get('upload_type_of', None)
        upload_id = int_or_none(validated_data.get('upload_id', None))
        created_by = self.context['created_by']
        created_from = self.context['created_from']
        created_from_is_public = self.context['created_from_is_public']

        # Save our object.
        image_upload = PublicImageUpload.objects.create(
            image_file=image_file,
            created_by=created_by,
            created_from=created_from,
            created_from_is_public=created_from_is_public,
        )

        # For debugging purposes only.
        logger.info("Created public image upload.")

        # Attach the uploaded image to the specific object type.
        if upload_type_of == "associate_avatar_image":
            obj = Associate.objects.get(id=upload_id)
            if obj.avatar_image:
                obj.avatar_image.delete()
            obj.avatar_image = image_upload
            obj.last_modified_from = self.context['created_from']
            obj.last_modified_from_is_public = self.context['created_from_is_public']
            obj.save()
            logger.info("Attached public image upload to associate.")

        if upload_type_of == "customer_avatar_image":
            obj = Customer.objects.get(id=upload_id)
            if obj.avatar_image:
                obj.avatar_image.delete()
            obj.avatar_image = image_upload
            obj.last_modified_from = self.context['created_from']
            obj.last_modified_from_is_public = self.context['created_from_is_public']
            obj.save()
            logger.info("Attached public image upload to customer.")

        if upload_type_of == "partner_avatar_image":
            obj = Partner.objects.get(id=upload_id)
            if obj.avatar_image:
                obj.avatar_image.delete()
            obj.avatar_image = image_upload
            obj.last_modified_from = self.context['created_from']
            obj.last_modified_from_is_public = self.context['created_from_is_public']
            obj.save()
            logger.info("Attached public image upload to partner.")

        if upload_type_of == "staff_avatar_image":
            obj = Staff.objects.get(id=upload_id)
            if obj.avatar_image:
                obj.avatar_image.delete()
            obj.avatar_image = image_upload
            obj.last_modified_from = self.context['created_from']
            obj.last_modified_from_is_public = self.context['created_from_is_public']
            obj.save()
            logger.info("Attached public image upload to staff.")

        # Return our validated data.
        return validated_data
