# Generated by Django 4.0.3 on 2022-11-27 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writing', '0010_remove_writingassignment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='writingassignment',
            name='access_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='first_access_time'),
        ),
    ]
