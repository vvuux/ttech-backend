# Generated by Django 3.2.4 on 2021-10-26 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vnpay', '0003_order_bank'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payed_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
