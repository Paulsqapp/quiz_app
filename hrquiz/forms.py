from django import forms
from .models import Agency_firm, Applicant, Quiz_profile
from django_editorjs_fields import EditorJsWidget


class Agency_CreationForm(forms.ModelForm):

    class Meta:
        model = Agency_firm
        exclude = ['name', 'slug']
        

class Applicant_CreationForm(forms.ModelForm):

    class Meta:
        model = Applicant
        exclude = ['name']
        
class deleteform(forms.Form):
    firm_name = forms.BooleanField(label='Confirm deletion of account ')


class Quiz_profile_form(forms.ModelForm):

    class Meta:
        model = Quiz_profile
        fields=(
        'name', 'creator', 'start_date', 'end_date', 'description', 'short_desc', 'resource_link', 'payment', 'pass_mark'
        )
       