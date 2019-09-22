# -*- coding: utf-8 -*-
import csv
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


class PrivateFileUploadManager(models.Manager):
    def delete_all(self):
        items = PrivateFileUpload.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_private_file_upload_id_number():
    """Function will generate a unique big-int."""
    private_file_upload = PrivateFileUpload.objects.all().order_by('id').last();
    if private_file_upload:
        return private_file_upload.id + 1
    return 1


class PrivateFileUpload(models.Model):
    """
    Upload image class which is publically accessible to anonymous users
    and authenticated users.
    """
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_private_file_uploads'
        verbose_name = _('Private File Upload')
        verbose_name_plural = _('Private File Uploads')
        default_permissions = ()
        permissions = (
            ("can_get_private_file_uploads", "Can get private file uploads"),
            ("can_get_private_file_upload", "Can get private file upload"),
            ("can_post_private_file_upload", "Can create private file upload"),
            ("can_put_private_file_upload", "Can update private file upload"),
            ("can_delete_private_file_upload", "Can delete private file upload"),
        )

    objects = PrivateFileUploadManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_private_file_upload_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    associate = models.ForeignKey(
        'Associate',
        help_text=_('The associate whom this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    customer = models.ForeignKey(
        'Customer',
        help_text=_('The customer whom this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    work_order = models.ForeignKey(
        'WorkOrder',
        help_text=_('The worker order that this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    partner = models.ForeignKey(
        'Partner',
        help_text=_('The partner whom this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    staff = models.ForeignKey(
        'Staff',
        help_text=_('The staff whom this file belongs to.'),
        related_name="private_file_uploads",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    binary_file = models.FileField(
        upload_to = 'uploads/%Y/%m/%d/',
        help_text=_('The upload binary file.'),
        storage=PrivateMediaStorage()
    )
    title = models.CharField(
        _("Title"),
        max_length=63,
        help_text=_('The tile content of this upload.'),
        blank=True,
        null=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('The text content of this upload.'),
        blank=True,
        null=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags associated with this private file uploads.'),
        blank=True,
        related_name="private_file_uploads"
    )
    is_archived = models.BooleanField(
        _("Is Archived"),
        help_text=_('Indicates whether private file was archived.'),
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
        help_text=_('The user whom created this file.'),
        related_name="created_private_file_uploads",
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
        help_text=_('The user whom last modified this private file upload.'),
        related_name="last_modified_private_file_uploads",
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
        if self.binary_file:
            self.binary_file.delete()
        super(PrivateFileUpload, self).delete(*args, **kwargs) # Call the "real" delete() method
