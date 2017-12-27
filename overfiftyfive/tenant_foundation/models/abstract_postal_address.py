from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class AbstractPostalAddress(models.Model):
    """
    The mailing address.

    http://schema.org/PostalAddress
    """
    class Meta:
        abstract = True

    address_country = models.CharField(
        _("Address Country"),
        max_length=127,
        help_text=_('The country. For example, USA. You can also provide the two-letter <a href="https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements">ISO 3166-1 alpha-2</a> country code.'),
    )
    address_locality = models.CharField(
        _("Address Locaility"),
        max_length=127,
        help_text=_('The locality. For example, Mountain View.'),
    )
    address_region = models.CharField(
        _("Address Region"),
        max_length=127,
        help_text=_('The region. For example, CA.'),
    )
    post_office_box_number = models.CharField(
        _("Post Office Box Number"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )
    postal_code = models.CharField(
        _("Postal Code"),
        max_length=127,
        help_text=_('The postal code. For example, 94043.'),
        db_index=True,
        blank=True,
        null=True,
    )
    street_address = models.CharField(
        _("Street Address"),
        max_length=255,
        help_text=_('The street address. For example, 1600 Amphitheatre Pkwy.'),
    )
    street_address_extra = models.CharField(
        _("Street Address (Extra Line)"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )
