from django import forms
from .models import QnA, Creator, QuestionImage, Quiz_Qns

# richtext in forms to allow editing
# how to allow complex data like code and formulae

''' ----------- form to create quiz creator -----'''
class CreatorForm(forms.ModelForm):
    
    class Meta:
        model = Creator
        fields = ['display_name','bio','contact', 'profile_pic']

class CreatorUpdate(forms.ModelForm):
    
    class Meta:
        model = Creator
        fields = ['contact', 'profile_pic', 'bio']


''' create a category form users can create category '''


''' ------------ search form ----------'''
class QnASearchForm(forms.Form):
    #Google and others use q for search
    q = forms.CharField(label='Search for a quiz',
                        max_length=100, )


''' ------------ images upload form ----------'''
class Quiz_images_Form(forms.ModelForm):
       
    class Meta:
        model = QuestionImage
        fields = ['question_number','image',]

        widgets = {
            'image': forms.ClearableFileInput()
        }

''' ------ html quiz creation forms -----'''
''' ------------ part a ----------'''
class Html_QuizA(forms.ModelForm):
    creator = forms.CharField(max_length=255, required=True, )

    class Meta:
        model = QnA
        exclude = ['slug', 'published', 'results_correct',
                   'results_wrong', 'question_file', 'creator', 'answers_file', 'pass_rate', 'num_attempts', 'summary_result', 'avg_results', 'created']
        labels = {
            'name': 'Quiz Title',
            'resource_link': 'Link to external resources',
            'publish': 'Publish (check) or save as draft',
            'description': 'Description/Short notes',
            
        }
        help_text = {
            'description': 'A short description or notes about the quiz',
            'pass mark': 'As a percentage (50%) or number of questions to answer correct e.g 8'
        }


''' ------------ part b ----------'''
# 2 parts because of formsets
class Html_QuizB(forms.Form):
    choice = (('multipe','Multipe Choice'), ('text','Text'), ('choice','Choice'))
    diff_choice = (('beginer','Beginer/introduction'), ('intermediate','Intermediate'), ('advanced','Advanced'))
    number = forms.IntegerField()
    difficulty_level = forms.ChoiceField(choices=diff_choice, required=False)
    question = forms.CharField(widget= forms.Textarea()) #richtext, no images
    answer_type = forms.ChoiceField(choices=choice, label='question_type')
    hint = forms.CharField(widget=forms.Textarea(), required= False)
    explanation = forms.CharField(widget=forms.Textarea(), required=False)
    answer = forms.CharField(widget= forms.Textarea())
    choice_a = forms.CharField(max_length=255, required= False)
    choice_b = forms.CharField(max_length=255, required= False)
    choice_c = forms.CharField(max_length=255, required= False)
    choice_d = forms.CharField(max_length=255, required=False)
    choice_e = forms.CharField(max_length=255, required= False)
    choice_f = forms.CharField(max_length=255, required= False)
    choice_g = forms.CharField(max_length=255, required=False)


''' ------ form to upload excel File -----'''
class UploadForm(Html_QuizA):
    #help text and labels, images to accept multiple files
    # inheritance works
    excelFile = forms.FileField(
        label='Upload Excel file with quiz', required=True,)
    creator = forms.CharField(max_length=255, required=True, )

class Quiz_dbform(forms.ModelForm):
    class Meta:
        model = Quiz_Qns
        fields = '__all__'
        #field_classes = {    'ch_a':"form-control",        }


class deleteform(forms.Form):
    name = forms.BooleanField(label='Confirm deletion of account ')