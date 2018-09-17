import requests
import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command


logger = logging.getLogger(__name__)


@job
def update_balance_owing_amount_for_associates_func(params):  #TODO: UNIT TEST
    # alternate_name = validated_data.get('alternate_name', None) #TODO: Params

    """
    EXAMPLE:

    params = {
        'franchise_schema_name': 'comicscantina',
        'associate_id': 123
    }
    """

    call_command(
        'update_balance_owing_amount_for_associates',
        # schema_name,
        # name,
        verbosity=0
    )
