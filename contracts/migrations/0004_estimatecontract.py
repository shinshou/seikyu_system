# Generated by Django 3.1.5 on 2024-04-29 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0025_auto_20240421_0618'),
        ('contracts', '0003_auto_20240429_0819'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstimateContract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estimate_id', models.CharField(max_length=200)),
                ('created_at', models.DateField()),
                ('issue_date', models.DateField()),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('billing_no', models.TextField()),
                ('remarks', models.TextField(blank=True, null=True)),
                ('subject', models.TextField(blank=True, null=True)),
                ('fee', models.IntegerField(default=0)),
                ('payment_method', models.CharField(choices=[('TR', 'Transfer'), ('CR', 'Credit')], max_length=2)),
                ('transfer_account', models.CharField(blank=True, max_length=255, null=True)),
                ('person_in_charge', models.CharField(blank=True, max_length=200, null=True)),
                ('total_price', models.IntegerField(default=0)),
                ('own_company_name', models.TextField(blank=True, null=True)),
                ('own_company_postal_code', models.TextField(blank=True, null=True)),
                ('own_company_address', models.TextField(blank=True, null=True)),
                ('own_company_tel', models.TextField(blank=True, null=True)),
                ('own_company_mailaddress', models.TextField(blank=True, null=True)),
                ('own_company_invoice_no', models.TextField(blank=True, null=True)),
                ('available', models.CharField(blank=True, default='T', max_length=1, null=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='masterdata.customer')),
            ],
        ),
    ]
