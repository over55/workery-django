# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator

from shared_foundation.constants import *
from shared_foundation.models import SharedUser
from tenant_foundation.utils import *


class UnifiedSearchItemManager(models.Manager):
    def delete_all(self):
        items = UnifiedSearchItem.objects.all()
        for item in items.all():
            item.delete()

    def partial_text_search(self, keyword):
        """Function performs partial text search of various textfields."""
        return UnifiedSearchItem.objects.filter(
            Q(text__icontains=keyword) |
            Q(text__istartswith=keyword) |
            Q(text__iendswith=keyword) |
            Q(text__exact=keyword) |
            Q(text__icontains=keyword)
        )

    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return UnifiedSearchItem.objects.annotate(search=SearchVector('indexed_text'),).filter(search=keyword)

    def update_or_create_associate(self, associate):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(associate=associate)
            item.type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.ASSOCIATE
            item.description=str(associate)
            item.associate=associate
            item.text=associate.indexed_text
            item.created_at=associate.created
            item.created_by=associate.created_by
            item.created_from=associate.created_from
            item.created_from_is_public=associate.created_from_is_public
            item.last_modified_at=associate.last_modified
            item.last_modified_by=associate.last_modified_by
            item.last_modified_from=associate.last_modified_from
            item.last_modified_from_is_public=associate.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.ASSOCIATE,
                associate=associate,
                description=str(associate),
                text=associate.indexed_text,
                created_at=associate.created,
                created_by=associate.created_by,
                created_from=associate.created_from,
                created_from_is_public=associate.created_from_is_public,
                last_modified_at=associate.last_modified,
                last_modified_by=associate.last_modified_by,
                last_modified_from=associate.last_modified_from,
                last_modified_from_is_public=associate.last_modified_from_is_public,
            )
            was_created = True
        item.tags.set(associate.tags.all())
        return item, was_created

    def update_or_create_customer(self, customer):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(customer=customer)
            item.type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.CUSTOMER
            item.customer=customer
            item.description=str(customer)
            item.text=customer.indexed_text
            item.created_at=customer.created
            item.created_by=customer.created_by
            item.created_from=customer.created_from
            item.created_from_is_public=customer.created_from_is_public
            item.last_modified_at=customer.last_modified
            item.last_modified_by=customer.last_modified_by
            item.last_modified_from=customer.last_modified_from
            item.last_modified_from_is_public=customer.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.CUSTOMER,
                customer=customer,
                description=str(customer),
                text=customer.indexed_text,
                created_at=customer.created,
                created_by=customer.created_by,
                created_from=customer.created_from,
                created_from_is_public=customer.created_from_is_public,
                last_modified_at=customer.last_modified,
                last_modified_by=customer.last_modified_by,
                last_modified_from=customer.last_modified_from,
                last_modified_from_is_public=customer.last_modified_from_is_public,
            )
            was_created = True
        item.tags.set(customer.tags.all())
        return item, was_created

    def update_or_create_staff(self, staff):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(staff=staff)
            item.type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.STAFF
            item.staff=staff
            item.description=str(staff)
            item.text=staff.indexed_text
            item.created_at=staff.created
            item.created_by=staff.created_by
            item.created_from=staff.created_from
            item.created_from_is_public=staff.created_from_is_public
            item.last_modified_at=staff.last_modified
            item.last_modified_by=staff.last_modified_by
            item.last_modified_from=staff.last_modified_from
            item.last_modified_from_is_public=staff.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.STAFF,
                staff=staff,
                description=str(staff),
                text=staff.indexed_text,
                created_at=staff.created,
                created_by=staff.created_by,
                created_from=staff.created_from,
                created_from_is_public=staff.created_from_is_public,
                last_modified_at=staff.last_modified,
                last_modified_by=staff.last_modified_by,
                last_modified_from=staff.last_modified_from,
                last_modified_from_is_public=staff.last_modified_from_is_public,
            )
            was_created = True
        item.tags.set(staff.tags.all())
        return item, was_created

    def update_or_create_job(self, job):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(job=job)
            item.type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.JOB
            item.job=job
            item.description="Work Order #"+str(job.id)
            item.text=job.indexed_text
            item.created_at=job.created
            item.created_by=job.created_by
            item.created_from=job.created_from
            item.created_from_is_public=job.created_from_is_public
            item.last_modified_at=job.last_modified
            item.last_modified_by=job.last_modified_by
            item.last_modified_from=job.last_modified_from
            item.last_modified_from_is_public=job.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.JOB,
                job=job,
                description="Work Order #"+str(job.id),
                text=job.indexed_text,
                created_at=job.created,
                created_by=job.created_by,
                created_from=job.created_from,
                created_from_is_public=job.created_from_is_public,
                last_modified_at=job.last_modified,
                last_modified_by=job.last_modified_by,
                last_modified_from=job.last_modified_from,
                last_modified_from_is_public=job.last_modified_from_is_public,
            )
            was_created = True
        item.tags.set(job.tags.all())
        return item, was_created

    def update_or_create_partner(self, partner):
        try:
            was_created = False
            item = UnifiedSearchItem.objects.get(partner=partner)
            item.type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.PARTNER
            item.partner=partner
            item.description=str(partner)
            item.text=partner.indexed_text
            item.created_at=partner.created
            item.created_by=partner.created_by
            item.created_from=partner.created_from
            item.created_from_is_public=partner.created_from_is_public
            item.last_modified_at=partner.last_modified
            item.last_modified_by=partner.last_modified_by
            item.last_modified_from=partner.last_modified_from
            item.last_modified_from_is_public=partner.last_modified_from_is_public
            item.save()
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.PARTNER,
                partner=partner,
                description=str(partner),
                text=partner.indexed_text,
                created_at=partner.created,
                created_by=partner.created_by,
                created_from=partner.created_from,
                created_from_is_public=partner.created_from_is_public,
                last_modified_at=partner.last_modified,
                last_modified_by=partner.last_modified_by,
                last_modified_from=partner.last_modified_from,
                last_modified_from_is_public=partner.last_modified_from_is_public,
            )
            was_created = True
        item.tags.set(partner.tags.all())
        return item, was_created

    def update_or_create_file(self, file):
        try:
            item = UnifiedSearchItem.objects.get(file=file)
            item.type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.FILE
            item.file=file
            item.description=str(file)
            item.text=file.indexed_text
            item.created_at=file.created_at
            item.created_by=file.created_by
            item.created_from=file.created_from
            item.created_from_is_public=file.created_from_is_public
            item.last_modified_at=file.last_modified_at
            item.last_modified_by=file.last_modified_by
            item.last_modified_from=file.last_modified_from
            item.last_modified_from_is_public=file.last_modified_from_is_public
            item.save()
            was_created = False
        except UnifiedSearchItem.DoesNotExist:
            item = UnifiedSearchItem.objects.create(
                type_of=UnifiedSearchItem.UNIFIED_SEARCH_ITEM_TYPE_OF.FILE,
                file=file,
                description=str(file),
                text=file.indexed_text,
                created_at=file.created_at,
                created_by=file.created_by,
                created_from=file.created_from,
                created_from_is_public=file.created_from_is_public,
                last_modified_at=file.last_modified_at,
                last_modified_by=file.last_modified_by,
                last_modified_from=file.last_modified_from,
                last_modified_from_is_public=file.last_modified_from_is_public,
            )
            was_created = True
        item.tags.set(file.tags.all())
        return item, was_created


class UnifiedSearchItem(models.Model):

    """
    META
    """

    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_unified_search_items'
        verbose_name = _('Unified Search Item')
        verbose_name_plural = _('Unified Search Items')
        default_permissions = ()
        permissions = ()

    '''
    CONSTANTS
    '''

    class UNIFIED_SEARCH_ITEM_TYPE_OF:
        CUSTOMER = 1
        ASSOCIATE = 2
        STAFF = 3
        JOB = 4
        PARTNER = 5
        FILE = 6

    '''
    CHOICES
    '''

    UNIFIED_SEARCH_ITEM_TYPE_OF_CHOICES = (
        (UNIFIED_SEARCH_ITEM_TYPE_OF.CUSTOMER, _('Customer')),
        (UNIFIED_SEARCH_ITEM_TYPE_OF.ASSOCIATE, _('Associate')),
        (UNIFIED_SEARCH_ITEM_TYPE_OF.STAFF, _('Staff')),
        (UNIFIED_SEARCH_ITEM_TYPE_OF.JOB, _('Job')),
        (UNIFIED_SEARCH_ITEM_TYPE_OF.PARTNER, _('Partner')),
        (UNIFIED_SEARCH_ITEM_TYPE_OF.FILE, _('File')),
    )

    """
    OBJECT MANAGER
    """

    objects = UnifiedSearchItemManager()

    """
    FIELDS
    """

    # THE FOLLOWING FIELDS ARE USED FOR SEARCHING.

    text = models.CharField(
        _("Text"),
        max_length=2047,
        help_text=_('The searchable content text used by the keyword searcher function.'),
        blank=True,
        null=True,
        db_index=True,
        unique=True
    )
    tags = models.ManyToManyField(
        "Tag",
        help_text=_('The tags with this unified search item.'),
        blank=True,
        related_name="unified_search_items"
    )

    # THE FOLLOWING FIELDS ARE USED TO MAP OUR SEARCHABLE ITEM TO AN OBJECT.

    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of item this is.'),
        choices=UNIFIED_SEARCH_ITEM_TYPE_OF_CHOICES,
        db_index=True,
    )
    description = models.CharField(
        _("Description"),
        max_length=255,
        help_text=_('The title of the object to display.'),
        blank=True,
        null=True,
    )
    customer = models.OneToOneField(
        "Customer",
        help_text=_('The customer of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    associate = models.OneToOneField(
        "Associate",
        help_text=_('The associate of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    staff = models.OneToOneField(
        "Staff",
        help_text=_('The staff of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    job = models.OneToOneField(
        "WorkOrder",
        help_text=_('The work-order of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    partner = models.OneToOneField(
        "Partner",
        help_text=_('The partner of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    file = models.OneToOneField(
        "PrivateFileUpload",
        help_text=_('The file of this search item.'),
        related_name="unified_search_item",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    # THE FOLLOWING FIELDS ARE USED FOR SYSTEM PURPOSES.

    created_at = models.DateTimeField(
        _("Created At"),
        help_text=_('When the object was created.'),
        blank=True,
        null=True
    )
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="created_unified_search_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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
    last_modified_at = models.DateTimeField(
        _("Last Modified At"),
        help_text=_('When the object was last modified.'),
        blank=True,
        null=True
    )
    last_modified_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom modified this object last.'),
        related_name="last_modified_unified_search_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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

    """
    FUNCTIONS
    """

    def __str__(self):
        return str(self.description)

    def save(self, *args, **kwargs):
        '''
        Override our save functionality to add the following additional
        functionality:
        '''

        # DEVELOPERS NOTE:
        # Why are we doing this? We want to handle the situation that our
        # application inputs an indexted text which is too large; therefore,
        # we will automatically truncate it so this issue will not occur.
        self.text = Truncator(self.text).chars(2047)

        '''
        Run our `save` function.
        '''
        super(UnifiedSearchItem, self).save(*args, **kwargs)
