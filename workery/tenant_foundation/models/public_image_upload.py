# -*- coding: utf-8 -*-
import csv
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from django.conf import settings
from django.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from starterkit.utils import (
    get_random_string,
    generate_hash,
    int_or_none,
    float_or_none
)
from shared_foundation.models import SharedUser
from tenant_foundation.utils import *
from workery.s3utils import PublicMediaStorage


class PublicImageUploadManager(models.Manager):
    def delete_all(self):
        items = PublicImageUpload.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_public_image_upload_id_number():
    """Function will generate a unique big-int."""
    public_image_upload = PublicImageUpload.objects.all().order_by('id').last();
    if public_image_upload:
        return public_image_upload.id + 1
    return 1


class PublicImageUpload(models.Model):
    """
    Upload image class which is publically accessible to anonymous users
    and authenticated users.
    """
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_public_image_uploads'
        verbose_name = _('Public Image Upload')
        verbose_name_plural = _('Public Image Uploads')
        default_permissions = ()
        permissions = (
            ("can_get_public_image_uploads", "Can get public image uploads"),
            ("can_get_public_image_upload", "Can get public image upload"),
            ("can_post_public_image_upload", "Can create public image upload"),
            ("can_put_public_image_upload", "Can update public image upload"),
            ("can_delete_public_image_upload", "Can delete public image upload"),
        )

    objects = PublicImageUploadManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_public_image_upload_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    image_file = models.ImageField(
        upload_to = 'uploads/%Y/%m/%d/',
        help_text=_('The upload image.'),
        storage=PublicMediaStorage()
    )


    #
    #  SYSTEM
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this away log.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )

    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom last modified this away log.'),
        related_name="%(app_label)s_%(class)s_last_modified_by_related",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.pk)

    def delete(self, *args, **kwargs):
        """
            Overrided delete functionality to include deleting the s3 file
            that we have stored on the system. Currently the deletion funciton
            is missing this functionality as it's our responsibility to handle
            the local files.
        """
        if self.image_file:
            self.image_file.delete()
        super(PublicImageUpload, self).delete(*args, **kwargs) # Call the "real" delete() method
