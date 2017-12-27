# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AbstractGeoCoordinate(models.Model):
    """
    The geographic coordinates of a place or event.

    http://schema.org/GeoCoordinates
    """
    class Meta:
        abstract = True

    elevation = models.FloatField(
        _("Elevation"),
        help_text=_('The elevation of a location (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).'),
        blank=True,
        null=True
    )
    latitude = models.DecimalField(
        _("Latitude"),
        max_digits=8,
        decimal_places=3,
        help_text=_('The latitude of a location. For example 37.42242 (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).'),
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        _("Longitude"),
        max_digits=8,
        decimal_places=3,
        help_text=_('The longitude of a location. For example -122.08585 (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).'),
        blank=True,
        null=True
    )
    location = PointField(
        _("Location"),
        help_text=_('A longitude and latitude coordinates of this location.'),
        null=True,
        blank=True,
        srid=4326,
        db_index=True
    )
