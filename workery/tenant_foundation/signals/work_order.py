from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import WorkOrder, UnifiedSearchItem


@receiver(post_save, sender=WorkOrder)
def save_work_order(sender, instance, **kwargs):
    """
    Function will either update or create the `UnifiedSearchItem` object so
    we have a unified searchable record for all our data.
    """
    UnifiedSearchItem.objects.update_or_create_job(instance)
