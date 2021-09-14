from django.contrib import admin
from .models import Agency_firm, Applicant, Quiz_profile, Interview_quiz, Applicant_score
# Register your models here.
### editorjs widget no showing in admin
admin.site.register(Agency_firm)
admin.site.register(Applicant)
admin.site.register(Quiz_profile)
admin.site.register(Interview_quiz)
admin.site.register(Applicant_score)
