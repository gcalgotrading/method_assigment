# Generated by Django 4.1.7 on 2023-05-31 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payout_dashboard', '0002_entity_type_alter_entity_entity_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='ein',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
