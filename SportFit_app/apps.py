from django.apps import AppConfig


class SportfitAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SportFit_app'

    def ready(self):
        import SportFit_app.signals  # Import signals to ensure they are registered