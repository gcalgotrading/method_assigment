# Generated by Django 4.1.7 on 2023-06-01 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payout_dashboard', '0006_entity_dunkin_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=255)),
                ('destination', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
    ]