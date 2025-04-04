# Generated by Django 5.1.7 on 2025-04-01 05:22

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purpose', models.CharField(choices=[('deid', 'De-identification'), ('reid', 'Re-identification')], help_text='Purpose of the prompt', max_length=255, unique=True)),
                ('model', models.CharField(help_text='AI/LLM model to be used for this purpose', max_length=255)),
                ('prompt', models.TextField()),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Prompt',
                'verbose_name_plural': 'Prompts',
            },
        ),
    ]
