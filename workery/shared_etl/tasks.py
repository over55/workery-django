import requests
import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command


logger = logging.getLogger(__name__)


@job
def update_balance_owing_amount_for_associate_func(params):  #TODO: UNIT TEST
    franchise_schema_name = params.get('franchise_schema_name', None)
    associate_id = params.get('associate_id', None)
    call_command(
        'update_balance_owing_amount_for_associate',
        franchise_schema_name,
        associate_id,
        verbosity=0
    )
