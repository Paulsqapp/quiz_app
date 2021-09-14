from django.urls import path
from .views import *

app_name= 'hrquiz'

urlpatterns = [

    path('', All_Jobs.as_view(), name='alljobs'),
    path('detail/<slug:slug>', Detailed_JobView.as_view(), name='job_detail'),
    path('register/', Agency_registration.as_view(), name= 'agency_registration'),
    path('agency/update/<str:name>', Agency_Update.as_view(), name='agency_update'),
    path('agency/delete/<str:name>', Agency_Delete.as_view(), name='agency_delete'),
    path('register/<slug:slug>', Agency_DetailView.as_view(),
         name='agency_registration'),
    path('applicant-register/',Applicant_registration.as_view(),        name='applicant_registration'),
    path('applicant/update/<str:name>', Applicant_Update.as_view(),
         name='applicant_registration'),
    path('applicant/delete/<str:name>', Applicant_Delete.as_view(),
         name='applicant_registration'),
    # job quiz
    path('jobquiz/', quiz_profile, name='jobquiz'),
    path('jobquiz/update/<slug:slug>',
         Quiz_Profile_Update.as_view(), name='jobquiz_update'),
    path('jobquizb/<slug:slug>', job_quiz_b, name='jobquizb'),
    path('takequiz/<slug:slug>', take_quiz, name='jobquizb'),

]

# All_Jobs
