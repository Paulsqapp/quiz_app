"""quizapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# sitemaps
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from quiz.models import QnA
import debug_toolbar

info_dict = {
    'queryset': QnA.objects.only('short_desc', 'description')
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quiz.urls', namespace='qna')),
    path('jobs/', include('hrquiz.urls', namespace='hrquiz')),
    path('accounts/', include('allauth.urls', )),
    
    path('__debug__/', include(debug_toolbar.urls)),
    path('sitemap.xml', sitemap, {
        'sitemaps': {
            'quizzes': GenericSitemap(info_dict, priority=0.6)
        }
    }, name = 'django.contrib.sitemaps.views.sitemap')
]  
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
