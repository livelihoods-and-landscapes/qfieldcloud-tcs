# Generated by Django 2.2.6 on 2020-03-13 11:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0008_remove_fileversion_original_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileversion',
            name='uploaded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]