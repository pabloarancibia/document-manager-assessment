# Generated by Django 4.1.9 on 2023-07-12 21:28

from django.db import migrations, models
import file_versions.models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0002_fileversion_file_user_fileversion_url_file_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileversion",
            name="url_file",
            field=models.FileField(upload_to=file_versions.models.custom_directory_path),
        ),
    ]
