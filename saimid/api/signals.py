import secrets
import string

from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from saimid.api.endpoints import reid_instructions
from saimid.api.models import Prompt, PromptLabelChoices
from saimid.config.prompts import DEID_INSTRUCTIONS, USER_RESPONSE_PROMPT


@receiver(post_migrate)
def create_default_data(sender, **kwargs) -> None:
    # Only run for a specific app
    if sender.name == "saimid.api":
        # Create only if not exists
        if not Prompt.objects.filter(purpose=PromptLabelChoices.DEID).exists():
            Prompt.objects.create(
                purpose=PromptLabelChoices.DEID,
                model="models/gemini-2.0-flash-lite",
                prompt=DEID_INSTRUCTIONS,
            )

        if not Prompt.objects.filter(purpose=PromptLabelChoices.REID).exists():
            Prompt.objects.create(
                purpose=PromptLabelChoices.REID,
                model="models/gemini-2.0-flash-lite",
                prompt=reid_instructions("TOKENS"),
            )

        if not Prompt.objects.filter(purpose=PromptLabelChoices.RESPONSE).exists():
            Prompt.objects.create(
                purpose=PromptLabelChoices.RESPONSE,
                model="models/gemini-2.0-flash-lite",
                prompt=USER_RESPONSE_PROMPT,
            )

        # Create superuser if not exists
        # TODO: Remove this for prod version
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            username = "root"
            email = "jukka.hassinen@gmail.com"
            # Generate a secure random password

            # Define character sets for a strong password
            chars = string.ascii_letters + string.digits + string.punctuation
            password = "".join(secrets.choice(chars) for _ in range(16))

            print(
                f"Created superuser with password: {password}"
            )  # Log the password for initial setup

            User.objects.create_superuser(
                username=username, email=email, password=password
            )
