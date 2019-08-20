# -*- coding: utf-8 -*-
from tenant_api.views.order_crud.order import (
   WorkOrderListCreateAPIView,
   WorkOrderRetrieveUpdateDestroyAPIView
)
from tenant_api.views.order_crud.order_comment import WorkOrderCommentListCreateAPIView
from tenant_api.views.order_crud.ongoing_order import (
   OngoingWorkOrderListCreateAPIView,
   OngoingWorkOrderRetrieveUpdateDestroyAPIView
)
from tenant_api.views.order_crud.ongoing_order_comment import OngoingWorkOrderCommentListCreateAPIView
from tenant_api.views.order_crud.order_lite_update import WorkOrderLiteUpdateAPIView
