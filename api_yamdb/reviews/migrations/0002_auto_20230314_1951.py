# Generated by Django 3.2 on 2023-03-14 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='genre',
        ),
        migrations.AddField(
            model_name='title',
            name='genre',
            field=models.ManyToManyField(blank=True, null=True, related_name='genre', to='reviews.Genre', verbose_name='Жанр'),
        ),
    ]
