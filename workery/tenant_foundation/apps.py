from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TenantFoundationConfig(AppConfig):
    name = 'tenant_foundation'
    verbose_name = _('Tenant Foundation')

    def ready(self):
        import tenant_foundation.signals.associate  # noqa
        import tenant_foundation.signals.customer
        import tenant_foundation.signals.staff
        import tenant_foundation.signals.partner
        import tenant_foundation.signals.work_order
        import tenant_foundation.signals.private_file_upload
