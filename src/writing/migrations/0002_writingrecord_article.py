# Generated by Django 4.0.3 on 2022-11-13 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='writingrecord',
            name='article',
            field=models.TextField(default='', verbose_name='article'),
            preserve_default=False,
        ),
    ]
