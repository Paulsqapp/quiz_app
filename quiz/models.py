from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from datetime import datetime

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

#from django.contrib.postgres.indexes import GinIndex

# Create your models here.
# separate what is returned (__str__) vs what is displayed on the admin (list_display)

User = get_user_model()  # if it fails, try settings.AUTH_USER_MODEL

# image upload handler
def image_path(instance, filename):  # USED FOR IDENTIFICATION & ASSOCIATION
    return f'image/{instance.name}/{filename}'


def quiz_image_path(instance, filename):  # USED FOR IDENTIFICATION & ASSOCIATION
    return f'image/{instance.quiz_name}/{filename}'

def thumbnail_path(instance, filename):  # USED FOR IDENTIFICATION & ASSOCIATION
    return f'thumbnail/{instance.self.quiz_name}/{filename}'

#document

def ref_doc_path(instance, filename):
    return f'doc/{instance.name}/{filename}'


def my_default():  # create a df.to_json for this. index, number and count
    '''
        sum_results = pd.DataFrame(columns=['number', 'count'], index=[1])
        x = sum_results.to_json(orient='index')
        x
        '{"1":{"number":null,"count":null}}'
    '''
    return {}

#create model managers for Qna

class Creator(models.Model):
    ''' 
    add display name
    '''
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150, unique=True)
    bio = models.TextField(null=True, blank=True)
    contact = models.CharField('Email or Social media contact', max_length=255, null= True, blank= True)
    profile_pic = ProcessedImageField(upload_to=image_path,
                                      processors=[ResizeToFill(100, 100)],
                                      format='JPEG',
                                      options={'quality': 60},
                                      null= True, blank= True )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Creator'
        verbose_name_plural = 'Creators'

#category class.

class Category(models.Model):
    
    main = models.CharField('Main Category name',
                            max_length=100, default='main', unique=True)
    
    def __str__(self):
        return self.main

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Sub_Category(models.Model):
    
    main = models.ForeignKey(Category, on_delete=models.PROTECT)
    sub_category = models.CharField('Sub Category name', max_length=100, default='sub-category', unique=True)

    def __str__(self):
        return sub_category

    class Meta:
        verbose_name = 'Sub_Category'
        verbose_name_plural='Sub_Categories'


class QnA(models.Model):
    '''
    query manager for published article -- publish between start and end
    '''
    class NewManager(models.Manager):
        time = timezone.now()  # publish=True, start_date__lte=time, end_date__gte=time
        def get_queryset(self):
            return super().get_queryset().filter(publish=True, start_date__lte=self.time, end_date__gte=self.time)

    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, blank=True)
    name = models.CharField(max_length=255, unique=True)  # unique
    slug = models.SlugField(max_length=255)
    short_desc = models.CharField('Short description/abstract for search optimisation', max_length=255, null=True, blank=True, default='Short quiz')
    description = RichTextField('Note to guide or assist those taking the quiz',null=True, blank=True)
    question_file = models.JSONField(
        default=my_default, null=True, blank=True)  # default

    resource_link = models.CharField(max_length=150, null=True, blank=True)
    payment = models.BooleanField(default=False)

    #audit
    created = models.DateTimeField(auto_now_add=True,)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    publish = models.BooleanField(default=False)
    
    # answers
    answers_file = models.JSONField(
        default=my_default, null=True, blank=True)

    # statistics
    summary_result = models.JSONField(
        default=my_default, null=True, blank=True)  # only for paid results
    avg_results = models.PositiveIntegerField(null=True, blank=True)  # 50%
    num_attempts = models.PositiveIntegerField(null=True, blank=True, default = 0) #default = 0
    pass_mark = models.PositiveIntegerField(null=True, blank=True, default = 0) #default = 0
    pass_rate = models.PositiveIntegerField(null=True, blank=True, default = 0) #default = 0, max 100
    objects = models.Manager()
    newmanager = NewManager()

    def get_absolute_url(self):
        cbn = self.name.replace(' ', '-').lower()
        return reverse('qna:qtn_list', args=[cbn])  #  kwargs={'slug': self.slug}

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'QnA'
        verbose_name_plural = 'QnAs'
        ordering = ['-created', 'num_attempts']
        ''' leave for now
        indexes = [
            GinIndex(name='NewGinIndex', fields=[
                     'title'], opclasses=['gin_trgm_ops']),
        ]
        '''

class QuestionImage(models.Model):
    '''
    # where do richtext store their images
    match questions to images
    upload to not working
    '''
    quiz_name = models.ForeignKey(
        QnA, on_delete=models.CASCADE, null=True, blank=True)
    question_number = models.PositiveSmallIntegerField() # use number for matching
    image = models.ImageField(upload_to='quiz_images', null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to=thumbnail_path, null=True, blank=True)

    #path to images not working
    # using save method to generate thumbnails

    def __str__(self):
        return f'{self.question_number}'

    class Meta:
        verbose_name = 'QuestionImage'
        verbose_name_plural = 'QuestionImages'


# interview forms for hr
# WITH TIMER
# check ... use edit mode to create images to questions
 
class Quiz_Qns(models.Model):
    
    quiz_name = models.ForeignKey(QnA, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    
    #options
    choice = (('multipe', 'Multipe Choice'),
              ('text', 'Text'), ('choice', 'Choice'))
    diff_choice = (('beginer', 'Beginer/introduction'),
                   ('intermediate', 'Intermediate'), ('advanced', 'Advanced'))

    qtn_type = models.CharField(choices=choice, max_length=20)
    diff_level = models.CharField(choices=diff_choice, null=True, blank=True,  max_length=20)


    #using ckeditor fields
    question = RichTextField(null = True, blank=True) # required
    answer = models.TextField('Correct answer',null=True, blank=True) 
    explanation = models.TextField(null=True, blank=True)
    hint = RichTextField(null=True, blank=True)

    #choices
    ch_a = models.CharField('Choice A',
                     max_length=255, null = True, blank=True) 
    ch_b = models.CharField('Choice B',
                     max_length=255, null = True, blank=True)
    ch_c = models.CharField('Choice C',
                     max_length=255, null=True, blank=True)
    ch_d = models.CharField('Choice D',
                     max_length=255, null = True, blank=True)
    ch_e = models.CharField('Choice E',
                     max_length=255, null = True, blank=True)
    ch_f = models.CharField('Choice F',
                     max_length=255, null=True, blank=True)

    def __str__(self):
        #return f'{self.iquiz_name} : {self.number}'
        return f'{self.quiz_name} : {self.number}'

    class Meta:
        verbose_name = 'Quiz_Qns'
        verbose_name_plural = 'Quiz_Qns'
        ordering = ['quiz_name','number' ]


