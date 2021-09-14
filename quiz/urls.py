from django.urls import path
from django.views.generic.base import TemplateView
from . import views

app_name = 'qna'
# 
urlpatterns = [
    path('', views.home, name='home'),
    path('samplestats/', TemplateView.as_view(template_name='quiz/sample_stats.html'), name='sample_stats'),
    path('contactus/', TemplateView.as_view(template_name='quiz/contactus.html'), name='contactus'),
    #category
    path('category', views.Create_Category.as_view(), name='create_category'),
    path('category/<category>', views.CatListView.as_view(), name='cat_list'),
    #path('qimage/<int:quiz>', views.Quiz_Images.as_view(), name='quiz_images'),
    path('qimage', views.Quiz_Images2, name='quiz_images'),
     
    #creator
    path('creator/', views.Creator_registration.as_view(), name='creator'),
    path('creator/<str:name>',views.Single_creator_view.as_view(), name='creator_page'),
    path('creator/update/<slug>',
         views.Creator_update.as_view(), name='creator_update'),
    path('creator/delete/<str:name>',
         views.Creator_delete.as_view(), name='creator_delete'),
 
    #path('quizupload/', views.Qna_View.as_view(), name='qna_upload'), #quiz_upload
    path('search/', views.qna_search, name='qna_search'),
    path('quiz/<slug:slug>', views.question, name='qtn_list'), #quiz/quizname
    #path('myquestions/<slug:slug>', views.Qna_creator_list, name='my_qtn_list'), 
    
    path('stats/<quiz>', views.quiz_stats, name='quiz_stats'),
    path('webquiz/', views.html_quiz, name='webquiz'),
    path('webquiz_b/<slug:slug>', views.html_quiz_b, name='webquiz_b'),
    path('allquizzes/', views.All_quizzes.as_view(), name='all_quizzes'),
]
