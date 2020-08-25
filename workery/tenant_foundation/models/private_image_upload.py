# -*- coding: utf-8 -*-
import uuid
import phonenumbers
import pytz
from djmoney.money import Money
from datetime import date, datetime, timedelta
from sorl.thumbnail import ImageField
from django.conf import settings
from django.db import models
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from shared_foundation.models import SharedUser
from tenant_foundation.utils import *
from workery.s3utils import PrivateMediaStorage


class PrivateImageUploadManager(models.Manager):
    def delete_all(self):
        items = PrivateImageUpload.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_private_image_upload_id_number():
    """Function will generate a unique big-int."""
    private_image_upload = PrivateImageUpload.objects.all().order_by('id').last();
    if private_image_upload:
        return private_image_upload.id + 1
    return 1


class PrivateImageUpload(models.Model):
    """
    Upload image class which is publically accessible to anonymous users
    and authenticated users.
    """
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_private_image_uploads'
        verbose_name = _('Private Image Upload')
        verbose_name_plural = _('Private Image Uploads')
        default_permissions = ()
        permissions = (
            ("can_get_private_image_uploads", "Can get private image uploads"),
            ("can_get_private_image_upload", "Can get private image upload"),
            ("can_post_private_image_upload", "Can create private image upload"),
            ("can_put_private_image_upload", "Can update private image upload"),
            ("can_delete_private_image_upload", "Can delete private image upload"),
        )

    objects = PrivateImageUploadManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_private_image_upload_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    image_file = ImageField(
        upload_to = 'uploads/%Y/%m/%d/',
        help_text=_('The upload image.'),
        storage=PrivateMediaStorage()
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether private image was archived.'),
        default=False,
        blank=True,
        db_index=True
    )


    #
    #  SYSTEM
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this image.'),
        related_name="created_private_image_uploads",
        on_delete=models.SET_NULL,
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
        help_text=_('The user whom last modified this private image upload.'),
        related_name="last_modified_private_image_uploads",
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

    """
    Override the `save` function to support save cached searchable terms.
    """
    def save(self, *args, **kwargs):
        '''
        The following code will populate our indexed_custom search text with
        the latest model data before we save.
        '''

        if self.indexed_text == None or self.indexed_text == "":
            self.indexed_text = str(uuid.uuid4())

        '''
        Run our `save` function.
        '''
        super(PrivateImageUpload, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)

    def delete(self, *args, **kwargs):
        """
            Overrided delete functionality to include deleting the s3 image
            that we have stored on the system. Currently the deletion funciton
            is missing this functionality as it's our responsibility to handle
            the local images.
        """
        if self.data_image:
            self.data_image.delete()

        super(PrivateImageUpload, self).delete(*args, **kwargs) # Call the "real" delete() method
