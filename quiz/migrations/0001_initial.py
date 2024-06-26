# Generated by Django 3.1.7 on 2021-08-06 03:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import quiz.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main', models.CharField(default='main', max_length=100, verbose_name='Main Category name')),
                ('sub_category', models.CharField(default='sub-category', max_length=100, verbose_name='Sub Category name')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['main'],
            },
        ),
        migrations.CreateModel(
            name='Creator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Creator',
                'verbose_name_plural': 'Creators',
            },
        ),
        migrations.CreateModel(
            name='QuestionImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to=quiz.models.image_path)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to=quiz.models.thumbnail_path)),
            ],
            options={
                'verbose_name': 'QuestionImage',
                'verbose_name_plural': 'QuestionImages',
            },
        ),
        migrations.CreateModel(
            name='QnA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(max_length=255)),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('publish', models.BooleanField(default=False)),
                ('description', models.TextField()),
                ('question_file', models.JSONField(blank=True, default=quiz.models.my_default, null=True)),
                ('resource_link', models.CharField(blank=True, max_length=150, null=True)),
                ('payment', models.BooleanField(default=False)),
                ('answers_file', models.JSONField(blank=True, default=quiz.models.my_default, null=True)),
                ('summary_result', models.JSONField(blank=True, default=quiz.models.my_default, null=True)),
                ('avg_results', models.PositiveIntegerField(blank=True, null=True)),
                ('num_attempts', models.PositiveIntegerField(blank=True, null=True)),
                ('pass_mark', models.PositiveIntegerField(blank=True, null=True)),
                ('pass_rate', models.PositiveIntegerField(blank=True, null=True)),
                ('category', models.ManyToManyField(blank=True, to='quiz.Category')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.creator')),
                ('question_images', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.questionimage')),
            ],
            options={
                'verbose_name': 'QnA',
                'verbose_name_plural': 'QnAs',
                'ordering': ['publish'],
            },
        ),
    ]
