# -*- coding: utf-8 -*-
from shared_foundation import constants


def foundation_constants(request):
    """
    Context processor will attach all our constants to every template.
    """
    return {
        'constants': constants
    }


def me(request):
    """
    Context processor stores session variables for the user profile which
    was saved during the "login" API endpoint. If the user updates this profile
    then the session will be updated and newest data released here.
    """
    return {
        'private_api_key': request.session.get('me_token', None),
        'private_api_key_orig_iat': request.session.get('me_token_orig_iat', None),
        'schema_name': request.session.get('me_schema_name', None),
        'logged_in_user_id': request.session.get('me_user_id', None),
    }
