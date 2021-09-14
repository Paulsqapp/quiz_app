# Generated by Django 3.1.7 on 2021-08-06 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_auto_20210806_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='qna',
            name='question_images',
        ),
        migrations.AddField(
            model_name='questionimage',
            name='question_images',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.qna'),
        ),
    ]