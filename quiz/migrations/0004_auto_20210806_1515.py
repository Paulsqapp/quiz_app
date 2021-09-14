# Generated by Django 3.1.7 on 2021-08-06 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_auto_20210806_1106'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionimage',
            old_name='question_images',
            new_name='quiz_name',
        ),
        migrations.RemoveField(
            model_name='questionimage',
            name='name',
        ),
        migrations.AddField(
            model_name='questionimage',
            name='question_number',
            field=models.PositiveSmallIntegerField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]