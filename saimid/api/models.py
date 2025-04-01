import uuid
from datetime import datetime
from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

# Create your models here.


class PromptLabelChoices(models.TextChoices):
    """Label choices for the prompt."""

    DEID = "deid", _("De-identification")
    REID = "reid", _("Re-identification")
    RESPONSE = "response", _("The system prompt for the user question")


class ModelChoices(models.TextChoices):
    FLASH_20_LITE = "models/gemini-2.0-flash-lite", _("Gemini Flash 2.0 Lite")


@final
class Prompt(models.Model):
    id = models.UUIDField[uuid.UUID, uuid.UUID](
        primary_key=True, default=uuid.uuid4, editable=False
    )
    created_at = models.DateTimeField[datetime, datetime](auto_now_add=True)
    updated_at = models.DateTimeField[datetime, datetime](auto_now=True)
    purpose = models.CharField[str, str](
        max_length=255,
        null=False,
        blank=False,
        unique=True,
        help_text=_("Purpose of the prompt"),
        choices=PromptLabelChoices.choices,
    )
    model = models.CharField[str, str](
        max_length=255,
        null=False,
        blank=False,
        help_text=_("AI/LLM model to be used for this purpose"),
        choices=ModelChoices.choices,
    )
    prompt = models.TextField[str, str](
        null=False, blank=False, help_text="The prompt to be used."
    )
    history = HistoricalRecords()

    @final
    class Meta:
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"

    def __str__(self) -> str:
        return str(self.purpose)
