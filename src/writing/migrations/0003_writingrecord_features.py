# Generated by Django 4.0.3 on 2022-11-15 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writing', '0002_writingrecord_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='writingrecord',
            name='features',
            field=models.TextField(default='', verbose_name='features'),
            preserve_default=False,
        ),
    ]
