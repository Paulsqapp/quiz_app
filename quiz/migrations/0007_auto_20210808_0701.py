# Generated by Django 3.1.7 on 2021-08-08 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0006_auto_20210806_2208'),
    ]

    operations = [
        migrations.RenameField(
            model_name='qna',
            old_name='published',
            new_name='created',
        ),
        migrations.AddField(
            model_name='qna',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
