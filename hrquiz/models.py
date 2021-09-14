from ckeditor.fields import RichTextField
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django_countries.fields import CountryField
from django.utils import timezone
from quiz.models import QnA, Quiz_Qns,  my_default

# Create your models here.

User = get_user_model() 

def image_path(instance, filename):  # USED FOR IDENTIFICATION & ASSOCIATION
    return f'image/{instance.name}/{filename}'

'''
how to store the score of applicants
private quizes and email
'''

class Agency_firm(models.Model):
    # change name to agency representative
    agency_rep = models.OneToOneField(User, on_delete=models.CASCADE)#name of creator
    firm_name = models.CharField(
        'Your agency\'s name', max_length=255, null=True, blank=True, unique=True)#unique
    slug = models.SlugField()
    firm_bio = models.TextField('Tell us about your firm',null=True, blank=True)
    contact = models.CharField('Email or Social media contact', max_length=255,)
    org_logo = models.ImageField('Organisation logo', upload_to='image_path', null=True, blank=True) # do thumbnail generation
    country = CountryField(blank=True, null=True)
    phone_regex = RegexValidator(regex=r"^\+(?:[0-9]●?){6,14}[0-9]$", message=_(
        "Enter a valid international mobile phone number starting with +(country code)"))
    mobile_phone = models.CharField(validators=[phone_regex], verbose_name=_(
        "Mobile phone"), max_length=17, blank=True, null=True)

    def __str__(self):
        return self.firm_name

    class Meta:
        verbose_name = 'Agency_firm'
        verbose_name_plural = 'Agency_firms'
        
# applicant account ... continue
class Applicant(models.Model):
    ''' highest level of education '''

    name = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(
        'First Name', max_length=255,)
    last_name = models.CharField(
        'Last Name', max_length=255,)
    middle_name = models.CharField(
        'Other Name', max_length=255, null=True, blank=True)
    about_me = models.CharField(
        'A short bio about myself', max_length=255, null=True, blank=True)
    contact = models.EmailField('Your email address')
    phone_regex = RegexValidator(regex=r"^\+(?:[0-9]●?){6,14}[0-9]$", message=_(
        "Enter a valid international mobile phone number starting with +(country code)"))
    mobile_phone = models.CharField(validators=[phone_regex], verbose_name=_(
        "Mobile phone"), max_length=17)
    profile_pic = models.ImageField(
        'Profile picture', upload_to='image_path', null=True, blank=True)  # do thumbnail generation
    resume = models.FileField(upload_to='image_path',)
    cover_letter = models.TextField('Your Cover letter',)
    country = CountryField(blank=True, null=True)


    def __str__(self):
        return f'{self.first_name}  {self.last_name}'

    class Meta:
        verbose_name = 'applicant'
        verbose_name_plural = 'applicants'

# questions profile abstract file
class Quiz_info(models.Model):
    '''
    overide inherited field names
    change field names
    no resource link
    '''
    
    name = models.CharField(max_length=255, unique=True)  # job title
    slug = models.SlugField(max_length=255)
    short_desc = models.CharField('Short description for search optimisation', max_length = 255, default = 'Short quiz')
    description = RichTextField(null=True, blank=True)# Job description
    question_file=models.JSONField(default = my_default, null = True, blank = True)  # default

    resource_link=models.CharField(max_length = 150, null = True, blank = True)
    payment=models.BooleanField(default = False)

        #audit
    created=models.DateTimeField(auto_now_add = True,)
    start_date=models.DateTimeField(default = timezone.now)
    end_date=models.DateTimeField(default = timezone.now)
    publish=models.BooleanField(default = False)
    private = models.BooleanField(default=False)

        # answers
    answers_file=models.JSONField(
    default = my_default, null = True, blank = True)

        # statistics
    summary_result=models.JSONField(
    default = my_default, null = True, blank = True)  # only for paid results
    avg_results=models.PositiveIntegerField(null = True, blank = True)  # 50%
    num_attempts=models.PositiveIntegerField(null = True, blank = True, default = 0)  # default = 0
    pass_mark=models.PositiveIntegerField(null = True, blank = True, default = 0)  # default = 0
    pass_rate=models.PositiveIntegerField(null = True, blank = True, default = 0)  # default = 0, max 100
   
    '''
    def __str__(self):
        return self.name
    '''

    class Meta:
        abstract = True

# actual file
class Quiz_profile(Quiz_info): # aka Job_profile
    #duration  of quiz
    creator = models.ForeignKey(Agency_firm, on_delete=models.CASCADE,)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Job_profile'
        verbose_name_plural = 'Job_profiles'

#questions abstract file
class Quiz_questions(models.Model):
    
    #quiz_name = models.ForeignKey(QnA, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()

    #options
    choice = (('multipe', 'Multipe Choice'),
              ('text', 'Text'), ('choice', 'Choice'))
    diff_choice = (('beginer', 'Beginer/introduction'),
                   ('intermediate', 'Intermediate'), ('advanced', 'Advanced'))

    qtn_type = models.CharField(choices=choice, max_length=20)
    diff_level = models.CharField(
        choices=diff_choice, null=True, blank=True,  max_length=20)

    #using ckeditor fields
    question = RichTextField(null=True, blank=True)  # required
    answer = models.TextField('Correct answer', null=True, blank=True)
    explanation = RichTextField(null=True, blank=True)
    hint = RichTextField(null=True, blank=True)

    #choices
    ch_a = models.CharField('Choice A',
                            max_length=255, null=True, blank=True)
    ch_b = models.CharField('Choice B',
                            max_length=255, null=True, blank=True)
    ch_c = models.CharField('Choice C',
                            max_length=255, null=True, blank=True)
    ch_d = models.CharField('Choice D',
                            max_length=255, null=True, blank=True)
    ch_e = models.CharField('Choice E',
                            max_length=255, null=True, blank=True)
    ch_f = models.CharField('Choice F',
                            max_length=255, null=True, blank=True)

    
    class Meta:
        #verbose_name = 'Interview_quiz'
        #verbose_name_plural = 'Interview_quizzes'
        abstract = True

# actual questions
class Interview_quiz(Quiz_questions):
    quiz_name = models.ForeignKey(Quiz_profile, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.quiz_name} : {self.number}'

    class Meta:
        verbose_name = 'Interview_quiz'
        verbose_name_plural = 'Interview_quizs'

class Applicant_score(models.Model):
    ''' 
    applicant take test, store his score
    for text answers store in json
    '''
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz_profile, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True, blank=True, default=0)
    answers = models.JSONField(default=my_default, null=True, blank=True)

    def __str__(self):
        return f'{applicant} {quiz}'

    class Meta:
        verbose_name = 'Applicant_score'
        verbose_name_plural = 'Applicant_scores'


# job categories