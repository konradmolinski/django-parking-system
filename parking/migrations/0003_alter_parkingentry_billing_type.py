# Generated by Django 4.0.4 on 2022-05-18 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0002_alter_parkingentry_billing_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingentry',
            name='billing_type',
            field=models.CharField(max_length=50),
        ),
    ]
