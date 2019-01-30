# -*- coding: utf-8 -*-
from tenant_foundation import constants
from tenant_foundation.models import (
    WORK_ORDER_STATE,
    ACTIVITY_SHEET_ITEM_STATE,
    ONGOING_WORK_ORDER_STATE,
    Customer
)

def tenant_constants(request):
    """
    Context processor will attach all our constants to every template for the
    tenant app.
    """
    return {
        'tenant_constants': constants,
        'ACTIVITY_SHEET_ITEM_STATE': ACTIVITY_SHEET_ITEM_STATE,
        'WORK_ORDER_STATE': WORK_ORDER_STATE,
        'ONGOING_WORK_ORDER_STATE': ONGOING_WORK_ORDER_STATE,
        'CUSTOMER_STATE': Customer.CUSTOMER_STATE,
        'DEACTIVATION_REASON': Customer.DEACTIVATION_REASON,
    }
