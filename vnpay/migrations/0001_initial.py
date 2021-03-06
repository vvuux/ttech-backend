# Generated by Django 3.2.4 on 2021-10-23 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0003_bank_international'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(blank=True, choices=[('Thẻ ngân hàng', 'Thẻ ngân hàng'), ('Ví điện tử', 'Ví điện tử'), ('Thẻ thanh toán quốc tế', 'Thẻ thanh toán quốc tế')], max_length=50, null=True)),
                ('describe', models.TextField(max_length=100)),
                ('type', models.CharField(choices=[('Đặt cọc', 'Đặt cọc'), ('Thanh toán', 'Thanh toán')], max_length=20)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='project.project')),
            ],
        ),
    ]
