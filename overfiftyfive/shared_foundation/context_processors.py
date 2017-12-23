# -*- coding: utf-8 -*-
from shared_foundation import constants


def foundation_constants(request):
    """
    Context processor will attach all our constants to every template.
    """
    return {
        'constants': constants
    }
