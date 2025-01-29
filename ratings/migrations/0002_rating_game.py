# Generated by Django 5.1.5 on 2025-01-29 15:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_alter_game_options_game_is_draw_alter_game_status'),
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='game',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='games.game'),
            preserve_default=False,
        ),
    ]
