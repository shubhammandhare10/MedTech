# Generated by Django 3.0.4 on 2020-04-18 05:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patient',
            old_name='Asymmetry',
            new_name='Asymmetry_Irregular_shape',
        ),
    ]
