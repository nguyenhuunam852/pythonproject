# Generated by Django 3.1.3 on 2020-12-17 02:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('urlpage', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Library_Words',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('iduser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Library_Words_Web',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id_libword', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.library_words')),
                ('id_web', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='urlpage.urlspage')),
            ],
        ),
    ]
