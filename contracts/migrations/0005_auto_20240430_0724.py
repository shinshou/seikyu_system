# Generated by Django 3.1.5 on 2024-04-29 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0004_estimatecontract'),
    ]

    operations = [
        migrations.RenameField(
            model_name='estimatecontract',
            old_name='billing_no',
            new_name='estimate_no',
        ),
    ]
