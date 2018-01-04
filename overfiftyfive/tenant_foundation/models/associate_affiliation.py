# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from tenant_foundation.constants import *
from tenant_foundation.models import AbstractBigPk


class AssociateAffiliationManager(models.Manager):
    def delete_all(self):
        items = AssociateAffiliation.objects.all()
        for item in items.all():
            item.delete()


class AssociateAffiliation(AbstractBigPk):
    class Meta:
        app_label = 'tenant_foundation'
        db_table = 'o55_associate_affiliations'
        verbose_name = _('Associate Affiliation')
        verbose_name_plural = _('Associate Affiliation')

    objects = AssociateAffiliationManager()

    #
    #  CUSTOM FIELDS
    #

    associate = models.ForeignKey(
        "Associate",
        help_text=_('The associate of our reference.'),
        related_name="%(app_label)s_%(class)s_associate_related",
        on_delete=models.CASCADE
    )
    organization = models.ForeignKey(
        "Organization",
        help_text=_('The organization whom this user is affiliated to.'),
        related_name="%(app_label)s_%(class)s_organization_related",
        on_delete=models.CASCADE
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type Of"),
        help_text=_('The type of affilication this customer has with the organization.'),
        choices=AFFILIATION_TYPE_OF_CHOICES,
    )
