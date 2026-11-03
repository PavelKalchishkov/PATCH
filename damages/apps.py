from django.apps import AppConfig


class DamagesConfig(AppConfig):
    name = 'damages'

    def ready(self):
        from damages import signals  # noqa: F401  (connects the cost-estimate signal)
