# Generated by Django 5.1.5 on 2025-01-28 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_alter_game_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='result',
            field=models.JSONField(default=None, null=True),
        ),
    ]
