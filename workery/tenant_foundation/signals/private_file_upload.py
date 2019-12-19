from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import PrivateFileUpload, UnifiedSearchItem


@receiver(post_save, sender=PrivateFileUpload)
def save_file(sender, instance, **kwargs):
    """
    Function will either update or create the `UnifiedSearchItem` object so
    we have a unified searchable record for all our data.
    """
    UnifiedSearchItem.objects.update_or_create_file(instance)
