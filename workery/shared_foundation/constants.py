# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


# The domain of our application.
#

WORKERY_APP_HTTP_PROTOCOL = settings.WORKERY_APP_HTTP_PROTOCOL
WORKERY_APP_HTTP_DOMAIN = settings.WORKERY_APP_HTTP_DOMAIN


# The groups of our application.
#

EXECUTIVE_GROUP_ID = 1
MANAGEMENT_GROUP_ID = 2
FRONTLINE_GROUP_ID = 3
ASSOCIATE_GROUP_ID = 4
CUSTOMER_GROUP_ID = 5


# The default currency of our application.
#

WORKERY_APP_DEFAULT_MONEY_CURRENCY = settings.WORKERY_APP_DEFAULT_MONEY_CURRENCY


# The following constants are used by the "contant_point" models.
#

TELEPHONE_CONTACT_POINT_TYPE_OF_ID = 1
MOBILE_CONTACT_POINT_TYPE_OF_ID = 2
WORK_CONTACT_POINT_TYPE_OF_ID = 3

TELEPHONE_CONTACT_POINT_TYPE_OF_CHOICES = (
    (TELEPHONE_CONTACT_POINT_TYPE_OF_ID, _('Residential Customer')),
    (MOBILE_CONTACT_POINT_TYPE_OF_ID, _('Commercial Customer')),
    (WORK_CONTACT_POINT_TYPE_OF_ID, _('Unknown Customer'))
)
