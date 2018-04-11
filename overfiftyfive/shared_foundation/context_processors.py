# -*- coding: utf-8 -*-
from shared_foundation import constants


def shared_constants(request):
    """
    Context processor will attach all our constants to every template.
    """
    return {
        'shared_constants': constants
    }


def me(request):
    """
    Context processor stores session variables for the user profile which
    was saved during the "login" API endpoint. If the user updates this profile
    then the session will be updated and newest data released here.
    """
    if request.session is not None:
        # SECURITY: Fetch our one-time use information to be displayed to the user
        #           and then delete it after the user has seen it. We do this
        #           because we do not want the server to store any API keys.
        private_api_key = request.session.get('me_token', None)
        private_api_key_orig_iat = request.session.get('me_token_orig_iat', None)
        if private_api_key and private_api_key_orig_iat:
            request.session.pop('me_token')
            request.session.pop('me_token_orig_iat')

        return {
            # ONE-TIME STORAGE
            'private_api_key': private_api_key,
            'private_api_key_orig_iat': private_api_key_orig_iat,

            # PERMANENT STORAGE
            'schema_name': request.session.get('me_schema_name', None),
            'logged_in_user_id': request.session.get('me_user_id', None),
        }
    else:
        return {
            # ONE-TIME STORAGE
            'private_api_key': None,
            'private_api_key_orig_iat': None,

            # PERMANENT STORAGE
            'schema_name': None,
            'logged_in_user_id': None,
        }
