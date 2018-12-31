# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from shared_foundation.models import SharedUser
from shared_foundation.constants import *
from tenant_foundation.utils import *


class CustomerCommentManager(models.Manager):
    def delete_all(self):
        items = CustomerComment.objects.all()
        for item in items.all():
            item.delete()


@transaction.atomic
def increment_customer_comment_id_number():
    """Function will generate a unique big-int."""
    last_resource_item = CustomerComment.objects.all().order_by('id').last();
    if last_resource_item:
        return last_resource_item.id + 1
    return 1


class CustomerComment(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'workery_customer_comments'
        verbose_name = _('Customer Comment')
        verbose_name_plural = _('Customer Comments')
        ordering = ['-created_at']
        default_permissions = ()
        permissions = (
            ("can_get_customer_comments", "Can get customer comments"),
            ("can_get_customer_comment", "Can get customer comment"),
            ("can_post_customer_comment", "Can create customer comment"),
            ("can_put_customer_comment", "Can update customer comment"),
            ("can_delete_customer_comment", "Can delete customer comment"),
        )

    objects = CustomerCommentManager()
    id = models.BigAutoField(
       primary_key=True,
       default=increment_customer_comment_id_number,
       editable=False,
       db_index=True
    )

    #
    #  FIELDS
    #

    comment = models.ForeignKey(
        "Comment",
        help_text=_('The comment this item belongs to.'),
        related_name="%(app_label)s_%(class)s_comment_categories",
        on_delete=models.CASCADE,
    )
    about = models.ForeignKey(
        "Customer",
        help_text=_('The customer whom this comment is about.'),
        related_name="%(app_label)s_%(class)s_about_related",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.about)+" "+str(self.created_at)
