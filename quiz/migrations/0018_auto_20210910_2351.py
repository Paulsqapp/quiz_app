# Generated by Django 3.1.7 on 2021-09-10 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0017_auto_20210910_2346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creator',
            name='display_name',
            field=models.CharField(default='john doe', max_length=150, unique=True),
            preserve_default=False,
        ),
    ]
