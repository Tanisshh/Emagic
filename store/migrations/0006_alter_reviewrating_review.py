# Generated by Django 4.0.1 on 2022-06-19 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_reviewrating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewrating',
            name='review',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
