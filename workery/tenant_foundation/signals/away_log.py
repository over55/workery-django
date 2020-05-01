from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import AwayLog


@receiver(post_save, sender=AwayLog)
def save_away_log(sender, instance, **kwargs):
    # Clear all cached properties.
    instance.associate.invalidate_all()
