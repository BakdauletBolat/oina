# Generated by Django 5.1.5 on 2025-01-29 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_alter_game_result'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='game',
            name='is_draw',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.IntegerField(choices=[(0, 'Requested'), (1, 'Started'), (2, 'Result Awaiting'), (3, 'Finished'), (4, 'Cancelled')], default=0),
        ),
    ]
