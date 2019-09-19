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
from tenant_foundation.models import Customer
from tenant_foundation.utils import *
from workery.s3utils import PrivateMediaStorage


class CustomerFileUploadManager(models.Manager):
    def delete_all(self):
        items = CustomerFileUpload.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_customer_file_upload_id_number():
    """Function will generate a unique big-int."""
    customer_file_upload = CustomerFileUpload.objects.all().order_by('id').last();
    if customer_file_upload:
        return customer_file_upload.id + 1
    return 1


class CustomerFileUpload(models.Model):
    """
    Upload image class which is publically accessible to anonymous users
    and authenticated users.
    """
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_customer_file_uploads'
        verbose_name = _('Customer File Upload')
        verbose_name_plural = _('Customer File Uploads')
        default_permissions = ()
        permissions = (
            ("can_get_customer_file_uploads", "Can get customer file uploads"),
            ("can_get_customer_file_upload", "Can get customer file upload"),
            ("can_post_customer_file_upload", "Can create customer file upload"),
            ("can_put_customer_file_upload", "Can update customer file upload"),
            ("can_delete_customer_file_upload", "Can delete customer file upload"),
        )

    objects = CustomerFileUploadManager()
    id = models.BigAutoField(
       primary_key=True,
       default = increment_customer_file_upload_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    customer = models.ForeignKey(
        Customer,
        help_text=_('The customer whom this file belongs to.'),
        related_name="file_uploads",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    binary_file = models.FileField(
        upload_to = 'uploads/%Y/%m/%d/',
        help_text=_('The upload binary file.'),
        storage=PrivateMediaStorage()
    )


    #
    #  SYSTEM
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this file.'),
        related_name="created_customer_file_uploads",
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
        super(CustomerFileUpload, self).delete(*args, **kwargs) # Call the "real" delete() method
