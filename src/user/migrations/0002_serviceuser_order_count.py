# Generated by Django 5.0.1 on 2024-05-09 14:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceuser",
            name="order_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
