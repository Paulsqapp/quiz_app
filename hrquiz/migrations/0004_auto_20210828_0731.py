# Generated by Django 3.1.7 on 2021-08-28 04:31

from django.db import migrations, models
import quiz.models


class Migration(migrations.Migration):

    dependencies = [
        ('hrquiz', '0003_auto_20210828_0700'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agency_firm',
            old_name='name',
            new_name='agency_rep',
        ),
        migrations.AddField(
            model_name='applicant_score',
            name='answers',
            field=models.JSONField(blank=True, default=quiz.models.my_default, null=True),
        ),
        migrations.AlterField(
            model_name='agency_firm',
            name='firm_name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name="Your agency's name"),
        ),
    ]
