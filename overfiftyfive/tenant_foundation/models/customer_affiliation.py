# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tenant_foundation.constants import *


class CustomerAffiliationManager(models.Manager):
    def delete_all(self):
        items = CustomerAffiliation.objects.all()
        for item in items.all():
            item.delete()


class CustomerAffiliation(models.Model):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_customer_affiliations'
        verbose_name = _('Customer Affiliation')
        verbose_name_plural = _('Customer Affiliation')
        default_permissions = ()
        permissions = (
            ("can_get_customer_affiliations", "Can get customer affiliations"),
            ("can_get_customer_affiliation", "Can get customer affiliation"),
            ("can_post_customer_affiliation", "Can create customer affiliation"),
            ("can_put_customer_affiliation", "Can update customer affiliation"),
            ("can_delete_customer_affiliation", "Can delete customer affiliation"),
        )

    objects = CustomerAffiliationManager()

    #
    #  CUSTOM FIELDS
    #

    customer = models.ForeignKey(
        "Customer",
        help_text=_('The customer of our reference.'),
        related_name="%(app_label)s_%(class)s_customer_related",
        on_delete=models.CASCADE
    )
    organization = models.ForeignKey(
        "Organization",
        help_text=_('The organization whom this customer is affiliated with.'),
        related_name="%(app_label)s_%(class)s_organization_related",
        on_delete=models.CASCADE
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type Of"),
        help_text=_('The type of affilication this customer has with the organization.'),
        choices=AFFILIATION_TYPE_OF_CHOICES,
    )
