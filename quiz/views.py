from datetime import datetime
from django.core.serializers import serialize
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
#from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline, TrigramSimilarity, TrigramDistance
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.forms import formset_factory, modelform_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone 
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView

from .models import QnA, Creator, Category, QuestionImage, Quiz_Qns
from .forms import CreatorForm, UploadForm, QnASearchForm, Quiz_images_Form, Html_QuizB, Html_QuizA, Quiz_dbform,CreatorUpdate,deleteform
#from hrquiz.models import Quiz_profile

#from itertools import zip_longest
import copy
import json
import matplotlib as plt
from PIL import Image
import pandas as pd
import string
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

User = get_user_model()
# Create your views here.
# all error messages are labelled as msg


#home
def home(request):
    #print(get_current_site(request))
    return render(request, 'quiz/main002.html')

#server_error
def entry_not_found(request, exception):
    #print(get_current_site(request))
    return render(request, 'quiz/404.html')


def server_error(request, exception):
    #print(get_current_site(request))
    return render(request, 'quiz/500.html')
'''---------- function to register as creator ==done == ----------- ''' 

#thumbnail generator
def tnail_generator(img):
    #print(f'001 thumbnail generator {img}')
    try:
        image = Image.open(img)
        image.thumbnail((600,600))
        return img
    except:
        return None
class Creator_registration(LoginRequiredMixin,CreateView): # create a creator
    
    model = CreatorForm
    form_class = CreatorForm
    success_url = reverse_lazy('qna:home') 
    template_name = 'quiz/creator.html'  
    
    # def get __ initial value
    def get(self, request, *args, **kwargs):
        ''' it works. Initial value repalced '''
        #print(request.user)
        name = request.user
        
        if Creator.objects.filter(name__username = request.user).exists():
            return HttpResponsePermanentRedirect(reverse('qna:webquiz'))

        form = super().get_form() # unbounf form
        initial_base = self.get_initial()
        initial_base['name']= name
        form.initial = initial_base
        return render(request, self.template_name, {'form': form})

    # def post __ name ==  request.user
    def post(self, request, *args, **kwargs):
        form = self.get_form() # bound form
        #print('001', form)
        if form.is_valid():
            pre_save = form.save(commit= False)
            #if name in User.objects.all().values_list(): # not working
            pre_save.name = request.user 
            pre_save.save()
            return HttpResponseRedirect(reverse('qna:webquiz'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form})

'''
display all creators page is missing
'''
'''------- function to update creator ==mysteriously not working == ----------- '''
class Creator_update(LoginRequiredMixin, UpdateView):  
    model = Creator
    form_class = CreatorForm
    success_url = reverse_lazy('qna:creator')
    template_name = 'quiz/creator_update.html'
    context_object_name= 'form'
    
    def get(self,request, **kwargs): #['bio','contact', 'profile_pic']
        obj = Creator.objects.get(name__username = self.request.user)
        form = super().get_form()
        initial_base = self.get_initial()
        initial_base['bio'] = obj.bio
        initial_base['contact'] = obj.contact #display_name
        initial_base['profile_pic'] = obj.profile_pic
        initial_base['display_name'] = obj.display_name
        form.initial = initial_base
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        obj = Creator.objects.get(name__username = self.request.user)
        form = CreatorUpdate(request.POST,request.FILES, instance=obj)  # bound form
        #print('001', form, obj)
        if form.is_valid():
            #print(form.cleaned_data)
            pre_save = form.save(commit=False)
            #if name in User.objects.all().values_list(): # not working
            pre_save.name = request.user
            
            #pre_save.save()
            return HttpResponseRedirect(reverse('qna:home'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form})
 

''' -----------creator's page -----done---------'''
class Single_creator_view(ListView):
    ''' display all quizes that belongs to a particular creator
        ## change to display name
    '''
    #context_object_name = 'my_quiz'
    template_name = 'quiz/creator_quiz.html'
    paginate_by= 10

    def get(self, request, **kwargs ):
        time = timezone.now()
        #print(request.user)
        creator_name= self.kwargs['name']
        qna_name = QnA.objects.filter(
            Q(creator__name__username = self.kwargs['name']) |
            Q(creator__display_name = self.kwargs['name'])).filter(
                start_date__lte=time, end_date__gte=time).select_related('creator')
        ##print(qna_name)
        
        return render(request, self.template_name, {'qna_name': qna_name, 'creator_name':creator_name})

''' ----------- DELETE creator's page --------------'''
class Creator_delete(LoginRequiredMixin,DeleteView): # Delete a creator
    
    model = CreatorForm
     
    template_name = 'quiz/delete_creator.html'  
   
    
    def get(self, request, **kwargs):  # ['bio','contact', 'profile_pic']
        try:
            obj = Creator.objects.only('name','display_name').get(
                name__username=self.request.user, )
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('qna:creator'))
        form = deleteform()
        return render(request, self.template_name, {'form': form, 'obj':obj})

    def post(self, request, name, *args, **kwargs):
        #print(request.POST)
        try:
            obj = Creator.objects.only('name').get(
                name__username=self.request.user, )
        except:  # if user has no agency, redirect to create view
            return HttpResponseRedirect(reverse('qna:creator'))

        form = deleteform(request.POST)  # bound form
        #print('001', form)
        if form.is_valid():
            obj.delete()
            return HttpResponseRedirect(reverse('qna:home'))
        else:
            #error dict
            return render(request, self.template_name, {'form': form, 'obj':obj})


''' List of all quiz available'''
class All_quizzes(ListView):
    def get(self, request, **kwargs):
        time = timezone.now()
        quiz = QnA.objects.only('creator', 'name', 'short_desc','created', 'end_date','pass_mark', 'category').filter( start_date__lte=time, end_date__gte=time).select_related('creator')
        ##print(quiz)

        return render(request, 'quiz/allquizzes.html', {'quiz':quiz})

''' ---quiz statistics ----'''
@login_required
def quiz_stats(request, quiz):
    # to be continued
    # check if request.user is creator, then get starts
    # consider chart.js
    # show starts --> ajax fills canvas in page

    #creator = get_object_or_404(Creator, name= request.user) # 
    quiz = QnA.objects.only('name','summary_result','num_attempts', 'pass_mark', 'pass_rate','start_date').get(creator__name= request.user, slug= quiz)
    ##print('001', quiz)
    
    results = quiz.summary_result
    results2 = json.loads(results)
    rate = round((quiz.pass_rate/quiz.num_attempts) * 100, 1)
    from collections import OrderedDict
    results3 = OrderedDict(sorted(results2.items()))
    #print(results2, results3)
    return render(request, 'quiz/stats.html', {'quiz':quiz, 'results':results,'rate':rate, 'results2':results3 })

   
#create view for creating a category
'''------- 3 category functions ------'''
class Create_Category(LoginRequiredMixin,CreateView):
    model = Category
    fields = '__all__'
    template_name= 'quiz/create_category.html'
    success_url = reverse_lazy('qna:home') # how to return to page
    

class CatListView(ListView):
    ''' display all QnA that belongs to a particular category '''
    context_object_name= 'cat_list'
    template_name= 'quiz/category.html'
    #paginate_by= 1
    #pagination
    def get(self,request,category, **kwargs):
        time = timezone.now()  # timezone
        cat_name= category
        cat_list = (QnA.objects.only('slug','name','short_desc','created','end_date', 'creator')
            .filter(category__main=category)
            .filter(publish=True, start_date__lte=time, end_date__gte=time).select_related('creator'))
        
        #print('001',cat_name)
        return render(request, self.template_name, {'cat_list':  cat_list, 'cat_name':cat_name} )



'''------------ Searching ------more nltk imports----------'''
def qna_search(request):
    #search both category, creator and qna
    search_form = QnASearchForm()
    
    if 'q' in request.GET:
        #print(request.GET) 

        q = QnASearchForm(request.GET) # bound
        #print(q)
        if q.is_valid():
            q_ = q.cleaned_data['q']
            '''
            results = QnA.objects.annotate(similarity=TrigramSimilarity(
                'short_desc', q_),).filter(similarity__gte=0.1).order_by('-similarity').select_related('creator')
            #num_results = len(results)
            #pagination
            result_b = Creator.objects.annotate(search=SearchVector(
                'display_name', 'bio', config='english')).filter(search=q_).select_related('name')
            '''
            results = QnA.objects.filter(short_desc__icontains = q_).select_related('creator')
            result_b = Creator.objects.filter(
                display_name__icontains=q_).select_related('name')

            #print(results, result_b)
            #paginator = Paginator(results, 5) # queryset, no. of items per page
            #page_number = request.GET.get('page', 1) # no page in 1st search. no error
            #page_obj = paginator.get_page(page_number)
            ##print('--paginator--', paginator.page(1), page_number)
            #num_results = results.count()
            return render(request, 'quiz/search.html', {'search_form': search_form,
                                               'q': q_,  'results': results,'result_b':result_b})
    else:
        q = ''
        results = []
        return render(request, 'quiz/search.html', {'search_form': search_form})


''' --- upload of question images --unused--'''
def Quiz_Images2(request, quiz='test001'):
    #hide quiz id
    # media path not working
    # 'HTTP_REFERER' sometimes there/ sometimes not
    # update and delete images
    # change to inline_formset
    #print(request.META['REMOTE_ADDR'], request.META['PATH_INFO'],
          #request.META.keys(), '\n \n')  # look for referer
    Quiz_Images_Formset = formset_factory(Quiz_images_Form, extra=3, max_num=20)
    formb = QnASearchForm()
    extra_form = 3
    
    if request.method == 'POST':
        #
        #print(request.POST)
        # check for add form fields
        #m = request.FILES
        if 'add_images' in request.POST and request.POST['add_images'] == 'true':
            #print('-------extra form---------', )
            formset_copy = dict(copy.deepcopy(request.POST))
            extra_field= int(
                formset_copy['form-TOTAL_FORMS'][0]) + extra_form
            
            formset = Quiz_Images_Formset = formset_factory(Quiz_images_Form, extra=extra_field, max_num=20)
        else:
            quiz_name = QuestionImage.objects.filter(quiz_name__name ='test001')
            qz_nm = QnA.objects.get(name =quiz) # get or 404
            #print('QuestionImage', quiz_name, 'qz_nm', qz_nm )

            brr = Quiz_Images_Formset(request.POST, request.FILES)
            if brr.is_valid():
            #bulk save
                #mmm = request.FILES.getlist('image')  # returns []
                formset_dict = dict(copy.deepcopy(request.POST))
                #print('\n --------mmm--------', formset_dict)
                save_list = []
                new_dict = {}
                with transaction.atomic(): ### create a dict then save
                    for key, value in formset_dict.items():
                        #print('\n --------is valid--------', key, '\n', value)
                        if 'question_number' in key and len(value[0]) > 0 :
                            save_list.append(value[0])
                        if 'image' in key and len(value[0]) > 0:
                            save_list.append(value[0])
                        #print('####### saved list #######',save_list)
                        #pass save_list[1] to thumbnail software
                        if len(save_list) >= 2 :
                            #print('####### saved list22222 #######',save_list, )
                            new_dict[key] = QuestionImage(
                                quiz_name= qz_nm,
                                question_number = int(save_list[0]),
                                image = save_list[1]
                            )
                            save_list = []
                    for key, value in new_dict.items():
                        #print('-----new dict---- \n', key, value.image )
                        value.save()

            formset = Quiz_Images_Formset()
        return render(request, 'quiz/image_upload.html', {'formset': formset, 'formb': formb})
        '''
        <QueryDict: {'csrfmiddlewaretoken': ['ttinU4AtrONzlNawNBdQsWOB1Qo9Aj4v4kmPvDdlt9JCeTDG9DlacsQnY8Qy5Zab'], 'form-TOTAL_FORMS': ['3'], 'form-INITIAL_FORMS': ['0'], 'form-MIN_NUM_FORMS': ['0'], 'form-MAX_NUM_FORMS': ['20'], 
        'form-0-name': ['paul kuria'], 'form-0-image': ['IMG_20200809_033022.jpg'], 'form-1-name': ['paul kuria'], 'form-1-image': ['IMG_20200809_033219.jpg'], 'form-2-name': ['paul kuria'], 'form-2-image': ['IMG_20200809_033015.jpg'],  'q': ['form b']}
        >
        #pp = save_list[0]
                            #qn_num = int(pp)
                            qz_nm.questionimage_set.create(
                                question_number=5,
                                image=save_list[1]
                            )
        '''
        # get id of quiz, generate thumbnail and save
        

    else:
        formset = Quiz_Images_Formset()
    return render(request, 'quiz/image_upload.html', {'formset': formset, 'formb': formb})
    
''' --- html quiz detail creation page -------'''
@login_required
def html_quiz(request, slug='part_a'):
    # works like a charm

    form2 = modelform_factory(QnA, fields=(
        'category','name','start_date', 'end_date','short_desc','description', 'resource_link', 'payment', 'pass_mark'
        ))

    if request.method == 'POST':
        form_a =  form2(request.POST)
        
        if form_a.is_valid():
            presaved = form_a.save(commit=False)
            creator = Creator.objects.get(name= request.user) 
            presaved.creator = creator
            slug = form_a.cleaned_data['name']
            presaved.slug =  slug.replace(' ', '-').lower()
            presaved.save()
            quiz_name = slug.replace(' ', '-').lower()
            #print(quiz_name) #pass id

            return HttpResponsePermanentRedirect(reverse('qna:webquiz_b', args=([quiz_name])))    
        else:
            messages.error(request, form_a.errors)
            return render(request, 'quiz/create_webquiz.html', {'form': form_a})
    else:
        return render(request, 'quiz/create_webquiz.html', {'form': form2})
''' --'TO_DO-- edit part_a -----'''
''' ----- part b -- display quiz questions to fill --- '''
@login_required
def html_quiz_b(request, slug):
    # use slug to create instance 
    # creating original quiz 
    #
    quizformset = inlineformset_factory(QnA, Quiz_Qns, fields=(
        'number', 'qtn_type', 'diff_level', 'question', 'answer',
        'explanation','hint','ch_a','ch_b','ch_c', 'ch_d','ch_e','ch_f' ),
        max_num= 8, min_num=4, extra=1)

    quiz_instance = QnA.objects.get(slug = slug, creator__name=request.user)#DEFER/ONLY
    formset = quizformset(instance=quiz_instance)
   
    ''' create dict based on this question '''
    if request.method == 'POST':
        formset_b = quizformset(request.POST,request.FILES,instance=quiz_instance )
        ##print(len(formset_b), formset_b) 

        if formset_b.is_valid():
            # redirect to view quiz. def clean method for validation
            formset_b.save()
            #print('--------valiiiid----',len(formset_b.cleaned_data), formset_b.cleaned_data)
            messages.success(request, 'Questions saved, preview?')
            return HttpResponseRedirect(reverse('qna:webquiz_b', args=([slug])))
        
        else:
            #print('--------not valiiiid----',formset_b.errors)
            messages.error(request, formset_b.errors)
        return render(request, 'quiz/webquiz_upload.html', {'formset': formset, })
        #return HttpResponseRedirect(reverse('qna:webquiz_b', args=(quiz_name)))    
    else:
            
        return render(request, 'quiz/webquiz_upload.html', {'formset': formset, 'quiz_instance':quiz_instance })

''' take and view quizz '''
def question(request, slug):
    
    time = timezone.now()  # timezone
    ##print('i.question', time)
    quiz_info = QnA.objects.get(slug=slug, start_date__lte=time,end_date__gte=time )
    quiz = quiz_info.quiz_qns_set.filter(quiz_name__slug=slug)
    ##print('i.question', quiz_info.end_date)
    
    #quiz = Quiz_Qns.objects.filter(
    #    quiz_name__slug=slug).select_related('quiz_name')
    #for i in quiz:
    # #print(i.quiz_name.description)
    ##print(quiz)
    if request.method == 'POST':
        
        ##print(request.POST)
        quiz_df = pd.DataFrame(quiz.values())
        #print('001',quiz_df, quiz_df.columns)
        quiz_df.drop([x for x in quiz_df if x not in [
                     'answer', 'number', 'explanation']], axis='columns', inplace=True)
        x = quiz_df.loc[quiz_df['number'] == 2] # resuls in a row df
        #print(quiz_df, x.answer)
        sum_dict = {}
        #print('00001', len(quiz_info.summary_result))
        if len(quiz_info.summary_result) <= 3:
            #print('if statement')
            
            sum_dict_keys = quiz_df['number'].tolist()
            #print('if statement', sum_dict_keys )
            for item in sum_dict_keys:
                #print('if statement for ', sum_dict)
                sum_dict[item] = 0
            #print('if statement end ', type(json.dumps(sum_dict)), json.dumps(sum_dict))
            quiz_info.summary_result = json.dumps(sum_dict)
            quiz_info.save(update_fields=['summary_result'])
        #print('here')
        answers = dict(copy.deepcopy(request.POST))
        del(answers['csrfmiddlewaretoken'])
        sum_results = {}
        #if quiz_info.payment:
        #    sum_results =pd.read_json(quiz_info.summary_result, orient = 'index')
        ''' --------- marking ------------'''
        max_score = len(quiz_df)
        result_dict = {}
        score = 0
        for key, val in answers.items(): # val comes as a string, not list
            index, qtn_type, others = key.split('_')
            #print('----------index---------', index, type(index), val, answers)
            correct_ans = quiz_df.loc[quiz_df['number'] == int(index)].answer.values
            
            # duplicate question number results in a list containing the answers]
            expla = f'expl_{index}'
            if len(quiz_df.loc[quiz_df['number'] == int(index)].explanation.values[0]) >= 1:
                result_dict[expla] = quiz_df.loc[quiz_df['number']
                                                 == int(index)].explanation.values[0]
            #print('-----correct_ans-----\n', correct_ans)
            ##print('hererrrrrrrrrrrrrrrrrrrrrrrr', xp)
            if qtn_type == 'choice':
                #print('--xxx---correct_choice-----\n', correct_ans[0], val)
                k = key + '_' + val[0]
                if val[0] == correct_ans[0]:
                    
                    result_dict[k] = 'correct'
                    score = score + 1
                    try:
                        sum_results[index] = sum_results[index] + 1
                    except:
                        sum_results[index] = 1
                else:
                    result_dict[k] = 'wrong'

            elif qtn_type == 'multi': # id has an attribute of val .... '2_multi_2': ['a', 'b'],
                #print('--xxx---multi_choice-----\n', correct_ans[0], val)
                corr_list = correct_ans[0].split(',')
                corr_list.sort()
                if val == corr_list: # set score if all answers are correct
                    score = score + 1
                    result_dict[k] = 'correct'
                    try: 
                        sum_results[index] = sum_results[index] + 1
                    except:
                        sum_results[index] = 1
                for item in val: # marking
                    #print('00010',type(item), item, val, 'corr_list',corr_list)
                    k = key + '_' + item
                    if item in corr_list:
                        #print('multi corect---- ', item, ' correct ans ',correct_ans)
                        result_dict[k] = 'halfcorrect'
                        
                    else:
                        #print('multi wrong ---- ', item, ' correct ans ',correct_ans)
                        result_dict[k] = 'wrong'
            
            elif qtn_type == 'text':  # '4_text_4': ['loser'] &&&   ['a1']
                #print('correct-001',correct_ans,', submited-001',val)
                x = correct_ans[0].lower()
                y = val[0].lower()
                #print('correct-',x,', submited-',y)
                if y == x:
                    result_dict[key] = 'correct'
                    score = score + 1
                    try: 
                        sum_results[index] = sum_results[index] + 1
                    except:
                        sum_results[index] = 1
                elif x == None:
                    max_score -+ 1
                    result_dict[key] = 'unmarked'
                else:
                    result_dict[key] = 'wrong'
        
        quiz_marks = round((score/max_score) * 100, 2)
        result_dict['score'] = quiz_marks
        
        # update statistics
        #print('quiz_info.num_attempts', quiz_info.num_attempts, '\n quiz_info.pass_mark',quiz_info.pass_mark )

        quiz_info.num_attempts = F('num_attempts') + 1
        if quiz_marks >= quiz_info.pass_mark:
            quiz_info.pass_rate = F('pass_rate') + 1
             
        update_summary_result = json.loads(quiz_info.summary_result)
        #print('003',update_summary_result, sum_results)
        for item in sum_results:
            #print(f'for loop start {item}, update_summary_result {update_summary_result}' )
            if item in update_summary_result:
                update_summary_result[item] += sum_results[item]
            else:
                update_summary_result[item] = sum_results[item]
        #print('003-------b', update_summary_result)
        quiz_info.summary_result = json.dumps(update_summary_result)
        quiz_info.save()
        quiz_info.refresh_from_db()
        
        #return
        #print('-------vf---------', result_dict, score, '\n', sum_results, '\n brr', update_summary_result)
        return JsonResponse(result_dict)
                
    return render(request, 'quiz/quiz_template.html', {'quiz': quiz,'quiz_info': quiz_info, })


''' test views '''
def test_view(request, slug = 'bnj'):
    pass
