# Generated by Django 3.0.4 on 2020-04-22 07:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0008_auto_20200419_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='result',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]
