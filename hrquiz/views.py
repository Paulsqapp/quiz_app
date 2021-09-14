from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.forms import formset_factory, modelform_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
#
from .answer_basket import Answer_basket
from .models import Agency_firm, Applicant, Quiz_profile, Interview_quiz, Applicant_score
from .forms import Agency_CreationForm, Applicant_CreationForm, deleteform, Quiz_profile_form

# Create your views here.

''' ####### replace Agency with agency ####'''

''' ------------ create Agency agency view -==done==-------- '''
class Agency_registration(LoginRequiredMixin, CreateView):  # create a creator

    model = Agency_firm
    form_class = Agency_CreationForm
    template_name = 'hrquiz/Agency_creation.html'
    
    # def post __ name ==  request.user
    def post(self, request, *args, **kwargs):
        form = self.get_form()  # bound form 
        #print('001', form)
        if form.is_valid():
            pre_save = form.save(commit=False)
            pre_save.name = request.user
            slug_ = form.cleaned_data['firm_name']
            pre_save.slug = slug_.replace(' ','-').lower()
            pre_save.save()
            return HttpResponseRedirect(reverse('qna:webquiz'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form})


''' ----- update Agency agency view ------- '''
class Agency_Update(LoginRequiredMixin, UpdateView):  # update creator
    ## THUMBNAIL
    model = Agency_firm
    template_name = 'hrquiz/agency_creation.html'

    def get(self, request, name,  **kwargs):  # slug field
        #works ok
        try: # get agency associated with this user and slug
            obj = Agency_firm.objects.get(
                name__username=self.request.user, firm_name=name)
        except: # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:agency_registration'))

        form = Agency_CreationForm(instance=obj)
        return render(request, self.template_name, {'form': form})

    def post(self, request, name, *args, **kwargs):
        try:
            obj = Agency_firm.objects.get(
                name__username=self.request.user, firm_name=name)
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:agency_registration'))

        form = Agency_CreationForm(request.POST, request.FILES ,instance=obj)  # bound form
        print('001', form)
        if form.is_valid():
            pre_save = form.save(commit=False)
            pre_save.name = request.user
            slug_ = form.cleaned_data['firm_name']
            pre_save.slug = slug_.replace(' ', '-').lower()
            pre_save.save()
            return HttpResponseRedirect(reverse('qna:home'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form})

'''-------delete Agency ------ '''
class Agency_Delete(LoginRequiredMixin, DeleteView):  # delete creator
    
    model = Agency_firm
    template_name = 'hrquiz/confirm_delete.html'

    def get(self, request, name,  **kwargs):  # slug field
        #works ok
        try:  # get agency associated with this user and slug
            obj = Agency_firm.objects.only('firm_name').get(
                name__username=self.request.user, firm_name=name)
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:agency_registration'))

        form = deleteform()
        return render(request, self.template_name, {'form': form})

    def post(self, request, name, *args, **kwargs):
        print(request.POST)
        try:
            obj = Agency_firm.objects.only('firm_name').get(
                name__username=self.request.user, firm_name=name)
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:agency_registration'))

        form = deleteform(request.POST)  # bound form
        print('001', form)
        if form.is_valid():
            obj.delete()
            return HttpResponseRedirect(reverse('qna:home'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form, 'obj':obj})


'''-------detailview Agency ------ '''
class Agency_DetailView(DetailView):
    def get(self, request,slug, **kwargs):
       obj = Quiz_profile.objects.select_related(
           'creator').filter(creator__slug=slug)
       
       return render(request, 'hrquiz/agency_detail.html', {'obj': obj})

''' ------------ create applicant view --------- '''
class Applicant_registration(LoginRequiredMixin, CreateView):  # create applicant

    model = Applicant
    form_class = Applicant_CreationForm
    template_name = 'hrquiz/applicant_creation.html'

    # def post __ name ==  request.user

    def post(self, request, *args, **kwargs):
        form = self.get_form()  # bound form  ------files uploads****
        print('001', form)
        if form.is_valid():
            pre_save = form.save(commit=False)
            pre_save.name = request.user
            pre_save.save()
            return HttpResponseRedirect(reverse('qna:home'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form, 'obj': obj})


''' ------------ Update applicant view --------- '''
class Applicant_Update(LoginRequiredMixin, UpdateView):  # update applicant

    model = Applicant
    template_name = 'hrquiz/applicant_creation.html'

    def get(self, request, name,  **kwargs):  # slug field
        #works ok
        try:  # get agency associated with this user and slug
            obj = Applicant.objects.get(
                name__username=self.request.user)
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:applicant_registration'))

        form = Applicant_CreationForm(instance=obj)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        try:
            obj = Applicant.objects.get(
                name__username=self.request.user)
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:applicant_registration'))

        form = Applicant_CreationForm(request.POST,request.FILES, instance=obj)  # bound form
        print('001', form)
        if form.is_valid():
            pre_save = form.save(commit=False)
            pre_save.name = request.user
            pre_save.save()
            return HttpResponseRedirect(reverse('qna:home'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form, 'obj': obj})


''' ------------ delete applicant view --------- '''
class Applicant_Delete(LoginRequiredMixin, DeleteView):  # delete applicant
    
    model = Applicant
    template_name = 'hrquiz/confirm_delete.html'

    def get(self, request, name,  **kwargs):  # slug field
        #works ok
        try:  # get agency associated with this user and slug
            obj = Applicant.objects.get(
                name__username=self.request.user)
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:applicant_registration'))

        form = deleteform()
        return render(request, self.template_name, {'form': form, 'obj':obj})

    def post(self, request, name, *args, **kwargs):
        print(request.POST)
        try:
            obj = Applicant.objects.get(
                name__username=self.request.user)
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:applicant_registration'))

        form = deleteform(request.POST)  # bound form
        print('001', form)
        if form.is_valid():
            obj.delete()
            return HttpResponseRedirect(reverse('qna:home'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form, 'obj': obj})


''' --- html quiz detail/profile creation page -------'''
@login_required
def quiz_profile(request):

    form2 = modelform_factory(Quiz_profile, fields=(
        'name','start_date', 'end_date', 'description', 'short_desc', 'resource_link', 'payment', 'pass_mark', 
    ))

    if request.method == 'POST':
        form_a = form2(request.POST)
        
        if form_a.is_valid():
            print(request.user.username)
            presaved = form_a.save(commit=False)
            agency_rep = Agency_firm.objects.get(
                agency_rep=request.user)  #associate this quiz with an agency
            slug = form_a.cleaned_data['name'].replace(' ', '-').lower()
            start_date = form_a.cleaned_data['start_date']
            end_date = form_a.cleaned_data['end_date']

            presaved.creator = agency_rep
            presaved.slug = slug.replace(' ', '-').lower()
            presaved.start_date = start_date
            presaved.end_date = end_date
            presaved.save() 
            
            # if it dooesn't save error. try except message link
            return HttpResponsePermanentRedirect(reverse('hrquiz:jobquiz', args=([slug])))
        else:
            messages.error(request, form_a.errors)
            return render(request, 'hrquiz/jobquiz.html', {'form': form_a})
    else:
        return render(request, 'hrquiz/jobquiz.html', {'form': form2})

'''------ update job quiz----- '''
class Quiz_Profile_Update(LoginRequiredMixin, UpdateView):  # create a creator
    # payment. no refunds for early whatever
    # if previous duration >> new duration ask for payment on remainder
    model = Quiz_profile
    template_name = 'hrquiz/jobquiz.html'

    def get(self, request, slug,  **kwargs):  # slug field
        #works ok
        try:  # get agency associated with this user and slug
            obj = Quiz_profile.objects.get(
                creator__agency_rep=self.request.user, slug=slug)
            #slug=slug, creator__agency_rep=request.user
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:agency_registration'))

        form = Quiz_profile_form(instance=obj)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, slug, *args, **kwargs):
        try:  # get agency associated with this user and slug
            obj = Quiz_profile.objects.get(
                creator__agency_rep=self.request.user, slug=slug)
            #slug=slug, creator__agency_rep=request.user
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('hrquiz:agency_registration'))

        form = Quiz_profile_form(
            request.POST, request.FILES, instance=obj)  # bound form
            #send creator as hidden field
        
        if form.is_valid():
            print('001', form.cleaned_data)
            pre_save = form.save(commit=False)
            slug_ = form.cleaned_data['name']
            #pre_save.creator = obj.creator
            pre_save.slug = slug_.replace(' ', '-').lower()
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            pre_save.start_date = start_date
            pre_save.end_date = end_date
            pre_save.save()
            return HttpResponseRedirect(reverse('qna:home'))
            '''
             
            '''
        else:
            print(form.errors)
            return render(request, self.template_name, {'form': form})

   
@login_required
def job_quiz_b(request, slug): # create actual quiz
    
    quizformset = inlineformset_factory(Quiz_profile,Interview_quiz, fields=(
        'number', 'qtn_type', 'diff_level', 'question', 'answer',
        'explanation', 'hint', 'ch_a', 'ch_b', 'ch_c', 'ch_d', 'ch_e', 'ch_f'),
        max_num=8, min_num=4, extra=1)

    quiz_instance = Quiz_profile.objects.get(
        slug=slug, creator__agency_rep=request.user)  # DEFER/ONLY
    formset = quizformset(instance=quiz_instance)
    
    if request.method == 'POST':
        formset_b = quizformset(
            request.POST, request.FILES, instance=quiz_instance)

        if formset_b.is_valid():
            print('--------not valiiiid----',)
            formset_b.save()
            print('--------valiiiid----',
                  len(formset_b.cleaned_data), formset_b.cleaned_data)
            messages.info(request, 'Questions saved')
            return HttpResponseRedirect(reverse('hrquiz:job_detail', args=([slug])))

        else:
            print('--------not valiiiid----', formset_b.errors)
            messages.error(request, formset_b.errors)
        return render(request, 'hrquiz/job_quiz_b.html', {'formset': formset, })
    else:
        return render(request, 'hrquiz/job_quiz_b.html', {'formset': formset, })


''' ---- list all jobs available ---1 query achieved with get object '''
class All_Jobs(ListView):
    model = Quiz_profile
    context_object_name = 'jobs'
    #template_name= 'hrquiz/test.html'

    def get(self,request, **kwargs):
        jobs = Quiz_profile.objects.only('creator', 'name', 'short_desc','end_date').select_related('creator')

        return render(request, 'hrquiz/job_listings.html', {'jobs': jobs} )

''' ---- list one jobs available --- '''
class Detailed_JobView(DetailView):
    model = Quiz_profile
    context_object_name = 'jobs'
    #template_name= 'hrquiz/test.html'

    def get(self,request,slug, **kwargs):
        jobs = Quiz_profile.objects.only(
            'creator', 'name','end_date', 'description', ).select_related('creator').get(slug=slug)

        return render(request, 'hrquiz/job_detail.html', {'jobs': jobs} )
#an applicant who wants to apply for a job
# create quiz for applicant. 
# fill job and see/

def take_quiz(request, slug):
    # go to Interview_quiz get questions, time module
    # shuffle questions
    # check that user hasnt done this quiz
    # create a list of qn numbers, random.choice
    quiz = Interview_quiz.objects.only('quiz_name','number','question', 'hint', 'ch_a','ch_b',
                                       'ch_c', 'ch_d', 'ch_e', 'ch_f','qtn_type').filter(quiz_name__slug=slug,).select_related('quiz_name')
    
    #session
    quiz_session = request.session.get('qui_ssion','kuma')
    request.session['kuma'] = 'Mellisa Monroe'
    print(quiz_session, request.session['kuma'])
    mn = ['question','hint', 'ch_a','ch_b','ch_c', 'ch_d', 'ch_e', 'ch_f']
    print(mn.pop())
    b = Answer_basket(request)
    print(str(b))
    #Paginator
    '''
    paginator = Paginator(quiz, 1)
    page_number = request.GET.get('page', 1)  # no page in 1st search. no error
    page_obj = paginator.get_page(page_number)
    '''
    return render(request, 'hrquiz/test.html', {'quiz': quiz})
