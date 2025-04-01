from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "saimid.api"

    def ready(self) -> None:
        super().ready()
        import saimid.api.signals  # noqa: F401
