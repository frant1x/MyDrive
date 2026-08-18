from django.apps import AppConfig


class FilesConfig(AppConfig):
    name = "files"

    def ready(self):
        """Import signals to ensure they are registered when the app is ready."""
        import files.signals
