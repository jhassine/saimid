from django.contrib import admin

from saimid.api.models import Prompt


# Register your models here.
@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin[Prompt]):
    """Admin interface for managing Prompt models."""
