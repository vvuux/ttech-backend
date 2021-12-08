# Generated by Django 3.2.4 on 2021-11-04 22:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_auto_20211103_1819'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-created_date', 'deadline', '-progress']},
        ),
        migrations.AlterField(
            model_name='projectchangehistory',
            name='change_order',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.CreateModel(
            name='ProgressDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.CharField(max_length=300)),
                ('status', models.CharField(choices=[('Hoàn thành', 'Hoàn thành'), ('Chưa hoàn thành', 'Chưa hoàn thành')], default='Chưa hoàn thành', max_length=30)),
                ('done_time', models.DateTimeField(blank=True, editable=False, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='project.project')),
            ],
        ),
    ]
