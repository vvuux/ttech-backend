# Generated by Django 3.2.4 on 2021-10-22 13:28

from django.db import migrations, models
import project.models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('bankcode', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True)),
                ('bank', models.CharField(max_length=300, unique=True)),
                ('logo', models.ImageField(upload_to=project.models.bank_directory_path)),
            ],
        ),
    ]