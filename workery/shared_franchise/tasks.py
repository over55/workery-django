import requests
import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command


logger = logging.getLogger(__name__)


@job
def create_franchise_func(validated_data):  #TODO: UNIT TEST
    alternate_name = validated_data.get('alternate_name', None)
    name = validated_data.get('name', None)
    description = validated_data.get('description', False)
    address_country = validated_data.get('address_country', None)
    address_locality = validated_data.get('address_locality', None)
    address_region = validated_data.get('address_region', None)
    post_office_box_number = validated_data.get('post_office_box_number', None)
    postal_code = validated_data.get('postal_code', None)
    street_address = validated_data.get('street_address', None)
    street_address_extra = validated_data.get('street_address_extra', None)
    schema_name = validated_data.get('schema_name', None)
    timezone_name = validated_data.get('timezone_name', None)
    logger.info("Input data:", str(validated_data))
    call_command(
        'create_franchise',
        schema_name,
        name,
        alternate_name,
        description,
        address_country,
        address_locality,
        address_region,
        post_office_box_number,
        postal_code,
        street_address,
        street_address_extra,
        timezone_name,
        verbosity=0
    )
