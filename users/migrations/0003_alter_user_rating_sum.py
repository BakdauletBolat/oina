# Generated by Django 5.1.5 on 2025-01-26 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_lost_sum_user_photo_url_user_rating_sum_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='rating_sum',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=19),
        ),
    ]
