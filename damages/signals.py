from django.db.models.signals import post_save
from django.dispatch import receiver

from damages.models import DamageDetection
from damages.services import generate_boq


@receiver(post_save, sender=DamageDetection)
def build_cost_estimate(sender, instance, created, **kwargs):
    """Every detected damage gets its bill of quantities straight away; nobody has to ask for it."""
    if created:
        generate_boq(instance)
