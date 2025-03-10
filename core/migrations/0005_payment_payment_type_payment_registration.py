# Generated by Django 5.1.5 on 2025-03-09 15:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_carmake_carmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(choices=[('fine', 'Fine Payment'), ('renewal', 'Renewal Payment')], default='fine', max_length=20),
        ),
        migrations.AddField(
            model_name='payment',
            name='registration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.registration'),
        ),
    ]
