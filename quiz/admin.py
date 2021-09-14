
from django.contrib import admin
from .models import QnA, Creator, Category, QuestionImage, Quiz_Qns
# Register your models here.

admin.site.register(Creator)
admin.site.register(QnA)
admin.site.register(Category)
admin.site.register(QuestionImage)
admin.site.register(Quiz_Qns)
