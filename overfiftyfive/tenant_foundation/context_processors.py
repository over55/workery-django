# -*- coding: utf-8 -*-
from tenant_foundation import constants


def tenant_constants(request):
    """
    Context processor will attach all our constants to every template for the
    tenant app.
    """
    return {
        'tenant_constants': constants
    }
