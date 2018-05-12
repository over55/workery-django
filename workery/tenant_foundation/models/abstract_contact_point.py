# -*- coding: utf-8 -*-
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.constants import *


# Override the validator to have our custom message.
email_validator = EmailValidator(message=_("Invalid email"))


class AbstractContactPoint(models.Model):
    """
    A contact point—for example, a Customer Complaints department.

    http://schema.org/ContactPoint
    """
    class Meta:
        abstract = True

    area_served = models.CharField(
        _("Area Served"),
        max_length=127,
        help_text=_('The geographic area where a service or offered item is provided.'),
        blank=True,
        null=True,
    )
    available_language = models.CharField(
        _("Available Language"),
        max_length=127,
        help_text=_('A language someone may use with or at the item, service or place. Please use one of the language codes from the <a href="https://tools.ietf.org/html/bcp47">IETF BCP 47 standard</a>.'),
        null=True,
        blank=True,
    )
    contact_type = models.CharField(
        _("Contact Type"),
        max_length=127,
        help_text=_('A person or organization can have different contact points, for different purposes. For example, a sales contact point, a PR contact point and so on. This property is used to specify the kind of contact point.'),
        blank=True,
        null=True,
    )
    email = models.EmailField(
        _("Email"),
        help_text=_('Email address.'),
        null=True,
        blank=True,
        validators=[email_validator],
        db_index=True
    )
    fax_number = PhoneNumberField(
        _("Fax Number"),
        help_text=_('The fax number.'),
        blank=True,
        null=True
    )
    hours_available = models.ManyToManyField(
        "OpeningHoursSpecification",
        help_text=_('The hours during which this service or contact is available.'),
        blank=True,
        related_name="%(app_label)s_%(class)s_contact_point_hours_available_related"
    )
    product_supported = models.CharField(
        _("Product Supported"),
        max_length=31,
        help_text=_('The product or service this support contact point is related to (such as product support for a particular product line). This can be a specific product or product line (e.g. "iPhone") or a general category of products or services (e.g. "smartphones").'),
        blank=True,
        null=True,
        default='',
    )
    telephone = PhoneNumberField(
        _("Telephone"),
        help_text=_('The telephone number.'),
        blank=True,
        null=True,
        db_index=True,
    )

    #
    # CUSTOM FIELDS - These are not standard Schema.org fields!
    #

    telephone_type_of = models.PositiveSmallIntegerField(
        _("Telephone type of"),
        help_text=_('The type of phone this is. Ex: work, home, etc.'),
        default=TELEPHONE_CONTACT_POINT_TYPE_OF_ID,
        blank=True,
        choices=TELEPHONE_CONTACT_POINT_TYPE_OF_CHOICES,
    )
    telephone_extension = models.CharField(
        _("Telephone Extension"),
        max_length=31,
        help_text=_('The telephone number extension.'),
        blank=True,
        null=True,
        default='',
    )
    other_telephone = PhoneNumberField( # Not standard in Schema.org
        _("Other Telephone"),
        help_text=_('The alternative telephone number.'),
        db_index=True,
        blank=True,
        null=True
    )
    other_telephone_extension = models.CharField(
        _("Other Telephone Extension"),
        max_length=31,
        help_text=_('The alternative telephone extension number.'),
        blank=True,
        null=True,
        default='',
    )
    other_telephone_type_of = models.PositiveSmallIntegerField(
        _("Other telephone type of"),
        help_text=_('The type of phone the alternative telephone is. Ex: work, home, etc.'),
        default=TELEPHONE_CONTACT_POINT_TYPE_OF_ID,
        blank=True,
        choices=TELEPHONE_CONTACT_POINT_TYPE_OF_CHOICES,
    )
