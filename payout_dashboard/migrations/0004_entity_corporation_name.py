# Generated by Django 4.1.7 on 2023-05-31 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payout_dashboard', '0003_entity_ein'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='corporation_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]