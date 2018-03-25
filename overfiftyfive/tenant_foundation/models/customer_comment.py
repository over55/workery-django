# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tenant_foundation.constants import *
from shared_foundation.models.user import SharedUser


# class CustomerCommentManager(models.Manager):
#     def delete_all(self):
#         items = CustomerComment.objects.all()
#         for item in items.all():
#             item.delete()


class CustomerComment(models.Model):
    """
    A "through" model class.
    """
    class Meta:
        app_label = 'tenant_foundation'
        ordering = ('-created_at',)
        db_table = 'o55_customer_comments'
        verbose_name = _('Customer Comment')
        verbose_name_plural = _('Customer Comments')
        default_permissions = ()
        permissions = (
            ("can_get_customer_comments", "Can get customer comments"),
            ("can_get_customer_comment", "Can get customer comment"),
            ("can_post_customer_comment", "Can post customer comment"),
            ("can_put_customer_comment", "Can update customer comment"),
            ("can_delete_customer_comment", "Can delete customer comment"),
        )

    # objects = CustomerCommentManager()

    #
    #  CUSTOM FIELDS
    #

    customer = models.ForeignKey(
        "Customer",
        help_text=_('The customer of our reference.'),
        related_name="%(app_label)s_%(class)s_customer_related",
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        "Comment",
        help_text=_('The comment of our reference.'),
        related_name="%(app_label)s_%(class)s_comment_related",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        SharedUser,
        help_text=_('The user whom created this object.'),
        related_name="%(app_label)s_%(class)s_created_by_related",
        on_delete=models.CASCADE,
    )
