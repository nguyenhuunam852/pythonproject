# Generated by Django 3.1.3 on 2020-11-27 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urlpage', '0002_urlspage_is_done'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlspage',
            name='is_done',
            field=models.BooleanField(default=False),
        ),
    ]