# Generated by Django 3.1.2 on 2020-11-02 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urlpage', '0007_wordurls_available'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wordurls',
            name='checkpic',
        ),
        migrations.AddField(
            model_name='wordurls',
            name='piclink',
            field=models.CharField(default='', max_length=2000),
        ),
        migrations.DeleteModel(
            name='Words_picture',
        ),
    ]