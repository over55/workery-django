# -*- coding: utf-8 -*-
from tenant_api.views.partner_crud.partner_list_create import PartnerListCreateV2APIView
from tenant_api.views.partner_crud.partner_retrieve_update_destroy import PartnerRetrieveUpdateDestroyV2APIView
from tenant_api.views.partner_crud.partner_contact_update import PartnerContactUpdateAPIView
from tenant_api.views.partner_crud.partner_address_update import PartnerAddressUpdateAPIView
from tenant_api.views.partner_crud.partner_metrics_update import PartnerMetricsUpdateAPIView
from tenant_api.views.partner_crud.partner_file_upload import (
    PartnerFileUploadListCreateAPIView,
    PartnerFileUploadArchiveAPIView
)
