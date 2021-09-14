from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.forms import formset_factory, modelform_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone 
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, CreateView
from django.views.generic import DetailView, ListView

from .models import QnA, Creator, Category, QuestionImage, Quiz_Qns
from .forms import CreatorForm, UploadForm, QnASearchForm, Quiz_images_Form, Html_QuizB, Html_QuizA, Quiz_dbform

#from itertools import zip_longest
import copy
import json
#import matplotlib as plt
import pandas as pd
import string
#import nltk

User = get_user_model()
# Create your views here.
# all error messages are labelled as msg
'''
excel upload processor
'''
def Excel_Processor(ex, paid):
    '''
    basic. No formula are read.
    Question column is a must
    ## add number column if not present
    read only first sheet
    xxx replace null with empty string... None is used in templates
    # if question column is none drop entire row
    '''
    print('003',ex)
    if len(ex) == 0: return 'No Excel file was attached for upload'
    #counter = 0
    for item in ex:
        #print('foolop Excel_Processor==', type(item), counter)
        #counter = counter +1
        try:
            qn_df = pd.read_excel(item) #pandas can read only in for loop
        except:
            print('004 except',)
            msg = 'An error occurred during upload. Uploaded File is not a recognized excel file'
            return msg
        print('004',item)

    #qn_df.fillna('') didnt work

    if not paid and len(qn_df) > 55:
        return 'Max. number of questions for free version is 8'

    if len(qn_df) > 54: return 'Excel file contains more than 50 questions'
    print('005',qn_df,'dataframe length', len(qn_df))
    #data_sheet = {}
    # Question column is a must
    
    cols = [x.lower() for x in qn_df.columns]
    if 'question' not in cols:
        y = 'Error: Question column was not found on your Excel Sheet'
        return y
    '''
    if choice in column name. merge them into new column
    '''
    qn_df.columns = [x.lower() for x in qn_df.columns]
    choice_columns = [choice for choice in qn_df.columns if 'choice' in choice]
    answer_columns = [[
        ans for ans in qn_df.columns if 'ans' in ans][1]]
    explanation_columns = [
        explain for explain in qn_df.columns if 'expl' in explain]
    
    print('xxxxxxxxxxxxxxx', choice_columns, answer_columns, explanation_columns)

    qn_df['ans_options'] = list(# prevent key error
        zip( #pass a list of columns, take their values and merge/zip
            qn_df[choice_columns].values 
            )
        )
    print(qn_df['ans_options'])
    str_list = string.ascii_lowercase
    qn_df['ans_options'] = qn_df['ans_options'].apply(lambda x: [list(zip(str_list, opt)) for opt in x if x != None]) ### added and not tested
    print('after', qn_df['ans_options'])
    qn_df['indices'] = qn_df.index # used to return answers from template

    # create summary_result object. create an new df.
    if 'number' not in qn_df.columns:
        qn_df['number'] = qn_df.index +1

    sum_results = pd.DataFrame()
    sum_results['number'] = qn_df['number']
    sum_results['ans_count'] = 0 # initial values
    print(sum_results)

    #drop some columns
    dropped = choice_columns + answer_columns + explanation_columns
    print('dataframe columns ---------------- \n', qn_df.columns)
    ans_df = qn_df[answer_columns + explanation_columns] 
    #ans_df['number'] = qn_df['number']
    #ans_df.columns = [x.lower() for x in ans_df.columns]
    print('answers data frame ---------------- \n', ans_df)

    new_qn_df = qn_df.drop(dropped, axis='columns')
    
    new_qn_df['answer_type'] = new_qn_df['answer_type'].str.lower()
    print('questions data frame ---------------- \n', new_qn_df, '\n', new_qn_df.columns)

    ''' new data frame for answers and explanation  '''
    
    # convert to json and return 
    new_qn_json = new_qn_df.to_json(orient='records') 
    new_qn_json2 = json.loads(new_qn_json)

    ans_df_json = ans_df.to_json(orient='index')
    ans_df_json2 = json.loads(ans_df_json)

    sum_results_json = sum_results.to_json(orient='index') 
    sum_results_json2= json.loads(sum_results_json) ## review
    print('data sheet to summary results ****', sum_results_json2)
    #saved_excel = json.dumps(data_sheet)
    #print('0010', new_qn_json2, '\n', ans_df_json2)
    return new_qn_json2, ans_df_json2, sum_results_json2

#home
def home(request):
    return render(request, 'quiz/main.html')

'''---------- function to register as creator ----------- ''' 
# add login required
class Creator_registration(CreateView): # create a creator
    # add user field to charfield and use get. initialize with username
    # if change to a user not logged in.
    # security check___ username, logged in name and name input must match
    # request error__ can only access request in get and post method

    # new field boi
    model = CreatorForm
    form_class = CreatorForm
    success_url = reverse_lazy('qna:home') 
    template_name = 'quiz/creator.html'  
    
    # def get __ initial value
    def get(self, request, *args, **kwargs):
        ''' it works. Initial value repalced '''
        print(request.user)
        name = request.user
        form = super().get_form() # unbounf form
        initial_base = self.get_initial()
        initial_base['name']= name
        form.initial = initial_base
        return render(request, self.template_name, {'form': form})

    # def post __ name ==  request.user
    def post(self, request, *args, **kwargs):
        form = self.get_form() # bound form
        print('001', form)
        if form.is_valid():
            pre_save = form.save(commit= False)
            name = form.cleaned_data['name']
            print('002', name)
            #if name in User.objects.all().values_list(): # not working
            pre_save.name = request.user
            pre_save.save()
            return HttpResponse('Very valid')
            # httpresponseredirect throws an error, try with request
        else:
            #error dict
            return HttpResponse('Not valid')


''' -----------creator's page --------------'''
class Single_creator_view(ListView):
    ''' display all quizes that belongs to a particular creator'''
    #context_object_name = 'my_quiz'
    template_name = 'quiz/creator_quiz.html'
    #paginate_by= 10
    #pagination

    def get(self, request, **kwargs ):
        print(request.user)
        creator_name= self.kwargs['name']
        qna_name = QnA.objects.filter(
            creator__name__username=self.kwargs['name']).filter(publish=True)
        
        #if request.user == qna_name.creator: print('btttttttttt')

        return render(request, self.template_name, {'qna_name': qna_name, 'creator_name':creator_name})

''' ---quiz stats ----'''
def quiz_stats(request, quiz):
    # to be continued
    # check if request.user is creator, then get starts
    # consider chart.js
    # show starts --> ajax fills canvas in page

    creator = get_object_or_404(Creator, name= request.user) # 
    quiz = QnA.objects.only('summary_result','num_attempts', 'pass_mark', 'pass_rate').get(creator= creator, slug= quiz)
    print(quiz.num_attempts)
    x = pd.read_json(json.dumps(quiz.summary_result), orient= 'index')
    x.columns = ['Question Number', 'pass rate (%)']
    x['pass rate (%)']=x['pass rate (%)'].apply(lambda x: x / quiz.num_attempts *100  )
    y = x.to_html() # matplotlib required
    return render(request, 'quiz/test_q.html', {'quiz':quiz, 'x':x, 'y':y})

'''------- function to view creators ------- '''
def Qna_creator_list(request, slug):
    ''' for each name (in slug), display question
    view question .... same as everyone else
    edit link in view question page and this
    '''
    #it works
    qtn_list = QnA.objects.filter(creator__name__username =slug)
    print(qtn_list.query, )
    return render (request, 'quiz/qna_creator_list.html', {'qtn_list':qtn_list})


'''---------- function to upload excel sheet ----------- '''              
class Qna_View(CreateView): 
    # upload excel
    # pre fill creator with creator.
    # cannot change how? disabled field
    #upload handlers ... for excel and images
    ## leave as is. use for excel uploads

    model = QnA
    form_class = UploadForm
    success_url = reverse_lazy('qna:home') 
    template_name = 'quiz/quiz_uploadForm.html'
    
    def get(self, request, *args, **kwargs):
        ''' form label ordering '''
        print(request.GET)
        creator = request.user
        form = super().get_form() # unbounf form
        initial_base = self.get_initial()
        initial_base['creator'] = creator
        form.initial = initial_base
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()  # bound form
        print(request.FILES.keys())  # dict_keys(['images', 'excelFile'])
        print(request.POST)
        files = request.FILES.getlist('excelFile') #multiple files
        # [<InMemoryUploadedFile: QnA app.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)>]
        #print(files)
        if form.is_valid():
            paid = form.cleaned_data['payment']
            print(request.POST)
            
            print('---paid---', paid)
            question_sheet = Excel_Processor(files, paid)

            # if there is an error in Excel Processor. respond with msg
            if type(question_sheet) == type('abc'):
                # send message
                messages.error(self.request, f'{question_sheet}')
                print(question_sheet)
                return render(request, self.template_name, {'form': form})
                #HttpResponse(f'{question_sheet}')
            
            else:
                print('------here---------')
                pre_save = form.save(commit=False)
                creator = form.cleaned_data['creator']
                slug = form.cleaned_data['name'] # how to slugify
                #print('002', creator, slug)
                y = Creator.objects.get(name= request.user) 
                pre_save.creator = y
                pre_save.slug = slug.replace(' ', '-').lower() #.slugify replace space with - and strip punctuation
                pre_save.question_file = question_sheet[0]
                pre_save.answers_file = question_sheet[1]
                pre_save.summary_result = question_sheet[2]
                pre_save.save()
                #y = json.loads(question_sheet)
                #x = json.dumps(question_sheet, indent = 4)
                print('__________end_________')
                
                return HttpResponse('Very valid')
                # httpresponseredirect throws an error, try with request
                # redirect to page to view questions
        else:
            #error dict
            print(form.errors)
            return render(request, self.template_name, {'form': form})
        
'''
page to show creator questions
slug == creators name then query
edit page...
'''


'''-------- function to display quiz ----------'''
def question(request, slug):  # get to see the questions, post to process answers
    ''' to display questions and process answers
    how to save stats
    '''
    qtn01 = get_object_or_404(QnA, slug=slug, publish= True) #try and see

    ''' when submit is clicked, answers are sent here. Post'''
    if request.method =='POST':
        print('------REQUEST.POST--------- \n',request.POST)
        ans = qtn01.answers_file # get answer dict
        print('------ans--------- \n',ans)

        # turn queryset to dict to avoid unexpected behavior
        # bcoz request.POST is immutable
        user_ans = dict(copy.deepcopy(request.POST))
        
        ''' MARKING match users answers to ans '''
        # pass updating sum_results to a queue, async to be updated later
        del(user_ans['csrfmiddlewaretoken']) # o(1) operation
        print('------user answers---------\n',user_ans)
        # matching user_ans to ans
        # use users answers to do match
        wrong, right = 0,0
        results_dict = {}
        res_key = ''
        total_score = len(ans)  # number of total questions
        # you are marking submited answers
        sum_results_df = pd.DataFrame()

        if qtn01.payment and len(qtn01.summary_result) > 1: #chech payment first.   
            print('here-----------------') ####here
            sum_results_df = pd.read_json(json.dumps(qtn01.summary_result), orient= 'index') ### review
            print('brrrr xxxx \n',sum_results_df, 'sum_results_df.columns', sum_results_df.columns)
        
        for key, value in user_ans.items(): 
            key2 = key.split('_')  # key == 'ans_1'
            ans_type, index = key2[0], key2[1]
            print('-----start forloop=======',value, ans_type,index, type(index))
            assert index in ans.keys() # just in case.
            correct_ans = ans[index]['answer']
            results_dict['expl_'+ str(int(index) +1)] = ans[index]['explanation']
            #print('!!!! correct_ans !!!!!!', correct_ans, type(correct_ans )  )
            print('-----value=======',value, type(value))

            if 'ans' in ans_type:
                '''
                All answers match for result + 1, else just mark correct and wrong
                '''
                print('ans in ans_type:', [correct_ans], '==', value)
                if sorted([correct_ans]) == sorted(value): 
                    #correct answers. works well for len(1) answers
                    right += 1 
                    for opt in value:
                        results_dict['ans_'+index + '_' + opt] = 'correct'
                        if not sum_results_df.empty:
                            sum_results_df.iat[int(
                                index), 1] = sum_results_df.iat[int(index), 1] + 1
                else:
                    marker = False
                    for opt in value:
                        if opt in correct_ans:
                            results_dict['ans_'+index + '_' + opt] = 'correct'
                            marker = True
                            #print('brrrr2',qtn01.summary_result)

                        else:
                            results_dict['ans_'+index + '_' + opt] = 'wrong'

                    if marker == True:
                        if not sum_results_df.empty:
                            sum_results_df.iat[int(
                                index), 1] = sum_results_df.iat[int(index), 1] + 1

            elif 'text' in ans_type:
                if correct_ans == None:
                    total_score -= 1
                elif hash(correct_ans) == hash(''.join(value)):
                    results_dict['text_' + index ] = 'correct'
                    right += 1
                    if not sum_results_df.empty:
                            sum_results_df.iat[int(index), 1]= sum_results_df.iat[int(index), 1] + 1
                else:
                    results_dict['text_' + index] = 'wrong'

        user_score = (right / total_score) * 100

        #update sum_results
        if not sum_results_df.empty:
            qtn01.summary_result = json.loads(sum_results_df.to_json(orient='index'))
        print('final sum_results', qtn01.summary_result, '\n', sum_results_df )
        #update num_attempts with each post

        qtn01.num_attempts = F('num_attempts') + 1
        #print('qtn02.pass_mark', qtn01.pass_mark, qtn01.num_attempts)
        
        if right > qtn01.pass_mark or user_score > qtn01.pass_mark :
            qtn01.pass_rate = F('pass_rate') +1

        qtn01.save()
        qtn01.refresh_from_db()
        print('qtn02.pass_mark', qtn01.pass_mark, qtn01.num_attempts)
        #response
        results_dict['score'] = user_score
        print('------results dict---------\n','wrong', wrong, 'right',right,results_dict, user_score)
        return JsonResponse(results_dict)

        # done -- add explanation to response
        # corrected -- score tally is wrong. multiple choice should be 1 or none
        # if creator has paid ????? question and score +1. save pass rate

    else:
        # add edit button if request.user == creator
        qtn = qtn01.question_file # <class 'dict'> 
        qtn_slug = qtn01.slug
        print('------qtn--------- \n',type(qtn), qtn)
        #xy = pd.DataFrame(qtn)
        #print(xy.T)
        #qtn_ordered = {}  # key error for missing keys
    
        return render(request, 'quiz/question.html', {'qtn':qtn, 'qtn_slug':qtn_slug, 'qtn01':qtn01})
          
#create view for creating a category
'''------- 3 category functions ------'''
class Create_Category(CreateView):
    model = Category
    fields = '__all__'
    template_name= 'quiz/create_category.html'
    success_url = reverse_lazy('qna:home') # how to return to page
    

class CatListView(ListView):
    ''' display all QnA that belongs to a particular category '''
    context_object_name= 'cat_list'
    template_name= 'quiz/category.html'
    #paginate_by= 10
    #pagination
    def get_queryset(self, **kwargs):
        content = {
            'cat_name': self.kwargs['category'],
            'qna_name': QnA.objects.filter(category__main=self.kwargs['category']).filter(publish= True)
        }
        return content

def category_list(request):
    ''' shows a list of categories available 
        context processor
    '''
    cat_items = Category.objects.all()
    context = {
        'cat_items':cat_items
    }
    
    return context

'''------------ Searching ----------------'''
def qna_search(request):
    #search both category, creator and qna
    search_form = QnASearchForm()
    # print(request.GET)  <QueryDict: {'q': ['mary']}>
    
   
    if 'q' in request.GET:
        print(request.GET) 

        q = QnASearchForm(request.GET) # bound
        if q.is_valid():
           # nltk to remove stop words
            # advanced search techniques for postgres
            # we have to hit multiple times. one hit multiple results
            q = q.cleaned_data['q'] # get value
            
            #nltk, split q into words and lemmatize
            lemmatizer = WordNetLemmatizer()
            q_words = word_tokenize(q)
            q_lemmatize = [lemmatizer.lemmatize(word) for word in q_words ]
            print('qqqqqqqqqq', '|'.join(q_lemmatize))
            #results = QnA.objects.filter(name__icontains = q)
            #print('qqqqqqqqqq', results)
            #use an or statement
            query = SearchQuery(q, search_type='websearch')
            q_vector = SearchVector(
                'name', 'description','creator__name__username' )  # 'category__name' error -- duplicate results
            results = QnA.objects.annotate(
                search = q_vector,).filter(search = query,publish= True ).select_related('creator')
            #union
            #print('-----results----', results)
            # what is returned when a filter fails
            num_results = len(results)
            #pagination
            paginator = Paginator(results, 5) # queryset, no. of items per page
            page_number = request.GET.get('page', 1) # no page in 1st search. no error
            page_obj = paginator.get_page(page_number)
            print('--paginator--', paginator.page(1), page_number)
            
            return render(request, 'quiz/search.html', {'search_form': search_form,
                                               'q': q,  'results': page_obj, 'num_results': num_results})
    else:
        q = ''
        results = []
        return render(request, 'quiz/search.html', {'search_form': search_form})


''' --- upload of question images ----'''
def Quiz_Images2(request, quiz='test001'):
    #hide quiz id
    # media path not working
    # 'HTTP_REFERER' sometimes there/ sometimes not
    # update and delete images
    # change to inline_formset
    print(request.META['REMOTE_ADDR'], request.META['PATH_INFO'],
          request.META.keys(), '\n \n')  # look for referer
    Quiz_Images_Formset = formset_factory(Quiz_images_Form, extra=3, max_num=20)
    formb = QnASearchForm()
    extra_form = 3
    
    if request.method == 'POST':
        #
        print(request.POST)
        # check for add form fields
        #m = request.FILES
        if 'add_images' in request.POST and request.POST['add_images'] == 'true':
            print('-------extra form---------', )
            formset_copy = dict(copy.deepcopy(request.POST))
            extra_field= int(
                formset_copy['form-TOTAL_FORMS'][0]) + extra_form
            
            formset = Quiz_Images_Formset = formset_factory(Quiz_images_Form, extra=extra_field, max_num=20)
        else:
            quiz_name = QuestionImage.objects.filter(quiz_name__name ='test001')
            qz_nm = QnA.objects.get(name =quiz) # get or 404
            print('QuestionImage', quiz_name, 'qz_nm', qz_nm )

            brr = Quiz_Images_Formset(request.POST, request.FILES)
            if brr.is_valid():
            #bulk save
                #mmm = request.FILES.getlist('image')  # returns []
                formset_dict = dict(copy.deepcopy(request.POST))
                print('\n --------mmm--------', formset_dict)
                save_list = []
                new_dict = {}
                with transaction.atomic(): ### create a dict then save
                    for key, value in formset_dict.items():
                        print('\n --------is valid--------', key, '\n', value)
                        if 'question_number' in key and len(value[0]) > 0 :
                            save_list.append(value[0])
                        if 'image' in key and len(value[0]) > 0:
                            save_list.append(value[0])
                        print('####### saved list #######',save_list)
                        #pass save_list[1] to thumbnail software
                        if len(save_list) >= 2 :
                            print('####### saved list22222 #######',save_list, )
                            new_dict[key] = QuestionImage(
                                quiz_name= qz_nm,
                                question_number = int(save_list[0]),
                                image = save_list[1]
                            )
                            save_list = []
                    for key, value in new_dict.items():
                        print('-----new dict---- \n', key, value.image )
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
    
''' --- html quiz creation page ----'''
def html_quiz(request):
    form_a = Html_QuizA()
    #form_b = Html_QuizB()

    Quiz_Qtns_Formset = formset_factory(Html_QuizB, extra=1, min_num=1, max_num=20)
    formset = Quiz_Qtns_Formset(prefix= 'quiz')

    if request.method == 'POST':
        formA = Html_QuizA(request.POST)
        formB = Quiz_Qtns_Formset(request.POST, prefix = 'quiz')

        # add questions button
        ## how to add new questions witout erasing existing user data ???
        if 'add_qtn' in request.POST and request.POST['add_qtn'] == 'true':
            print('-------extra form---------',formB )
            formset_copy = dict(copy.deepcopy(formB))
            formset_copy['quiz-TOTAL_FORMS'] =  int(
                formset_copy['quiz-TOTAL_FORMS'][0]) + 1
                        
            formset = formset_factory(formset_copy)

            return render(request, 'quiz/test_q.html', {'form_a':formA, 'formset':formset})
        
        #print(formA, '\n', formB)

        if formA.is_valid() and formB.is_valid():
            print('----------xxxxxxxxxxx both forms are valid --------------')
            pre_saved = formA.save(commit=False)
            '''
            formA.cleaned_data == 
                {'category': <QuerySet [<Category: banking>]>, 'name': 'Kumangana 2', 'description': 'Lots of words in the description', 'resource_link': 'there', 'payment': True, 'publish': True, 'pass_mark': 55, 'creator': 'paul'}
            formB.cleaned_data ==
                 [{'number': 1, 'difficulty_level': 'beginer', 
                'question': 'cfvgb buhnjm xsdc qwer uio vcsdf', 'question_type': 'text', 
                'hint': 'kmjnbhvg cdfyguh qwertghbn', 'explanation': 'vgbhnjk vgbhjnk iuklpok ikj', 
                'answer': 'vgbhnjk vygbhnj cvgbhn', 
                'choice_a': 'Choice a',
                'choice_b': 'Choice b', 
                ...
                {'number': 1, 'difficulty_level': 'beginer', 
                'question': 'Will ana kubow use my app', 'question_type': 'text', 
                'hint': 'vgbhjn vbhjnk vgbhn', 'explanation': 'bghjnke j lk', 
                'answer': 'nfjfvfod njfdkmcld', ...
            '''
            #x = formB.cleaned_data['quiz-0-answer']
            #print('xxxx \n',  formB.cleaned_data)
            #quiz df
            quiz_df =pd.DataFrame(formB.cleaned_data, index= range(0,len(formB.cleaned_data)))
            print('quiz_df \n',  quiz_df)
            choice_columns = [choice for choice in quiz_df .columns if 'choice' in choice]
            # merge choices
            quiz_df['ans_options'] = list(zip(quiz_df[choice_columns].values))
            str_list = string.ascii_lowercase
            quiz_df['ans_options'] = quiz_df['ans_options'].apply(lambda x: [list(zip(str_list, opt)) for opt in x if x != None])
            quiz_df['indices'] = quiz_df.index 
            
            #ans df
            qz_ans_df = quiz_df[['indices','answer', 'explanation']] 
            
            quiz_df_2 = quiz_df.drop(['explanation', 'answer', 'choice_a', 'choice_b', 'choice_c', 'choice_d',
            'choice_e', 'choice_f', 'choice_g', ], axis= 'columns')

            # summary results
            sum_results = pd.DataFrame()
            sum_results['number'] = quiz_df_2['number']

            print('xxxx quiz_df_2 \n',  quiz_df_2)
            print('xxxx qz_ans_df \n',  qz_ans_df)
            print('xxxx sum_results \n',  sum_results)

            # to json
            quiz_json = quiz_df_2.to_json(orient= 'records')
            quiz_json2 = json.loads(quiz_json)

            ans_json = qz_ans_df.to_json(orient= 'index')
            ans_json2 = json.loads(ans_json)

            results_json = sum_results.to_json(orient='index')
            #results_json2 = json.loads(results_json)

            # saving to db
            pre_saved.question_file = quiz_json2
            pre_saved.answers_file = ans_json2
            pre_saved.summary_result = results_json
            y = Creator.objects.get(name= request.user) 
            pre_saved.creator = y

            pre_saved.save()

            return HttpResponse('Very Valid')
            #return render(request, 'quiz/test_2.html', {'formB': y})
            #process formB
        else:
            #xy = pd.read_html(formB)
            print('vvvvvvvvvv',formA.errors, formB.errors )
    return render(request, 'quiz/test_q.html', {'form_a':form_a, 'formset':formset})

def test_view(request):
    #form = Quiz_dbform()
    #form2 = modelform_factory(QnA, fields='__all__') # a single modelform
    '''
    <QueryDict: {'csrfmiddlewaretoken': ['gaSwyRjYxOr90bOhvn4R5TUKFLVeQSXcR1WY9qWQz9ncThhrRpcbPpWwC3nDly3S'], 'creator': ['4'], 'category': ['5'], 'name': ['nm'], 'slug': ['nm'], 'description': ['nm,'], 'question_file': ['{}'], 'initial-question_file': ['{}'], 'resource_link': [''], 'created': ['2021-08-15 14:50:45'], 'initial-created': ['2021-08-15 14:50:45'], 'answers_file': ['{}'], 'initial-answers_file': ['{}'], 'summary_result': ['{}'], 'initial-summary_result': ['{}'], 'avg_results': [''], 'num_attempts': [''], 'pass_mark': [''], 'pass_rate': ['']}>
    '''
    #form3 = modelformset_factory(QnA, fields='__all__') # lists all items in db plus additional extra field. good for editing

    quizformset = inlineformset_factory(QnA, Quiz_Qns, fields=(
        'quiz_name', 'number', 'qtn_type', 'diff_level', 'question', 'answer',
        'explanation','hint','ch_a','ch_b','ch_c', 'ch_d','ch_e','ch_f' ),
        max_num= 4, extra=1)
    #creator = QnA.objects.get(name = 'quiz 001', creator__name= request.user ) # get or create
    #form4 = quizformset(instance=creator)
    #print(request.POST)
    '''
    if request.method == 'POST':
        # BOUND FORMSET
        form4 = quizformset(request.POST, request.FILES, instance=creator)
        if form4.is_valid():
            form4.save()
    '''
    # to view questions
    quizz = Quiz_Qns.objects.filter(
        quiz_name__name='quiz 001').defer('explanation','answer')
    
    if request.method == 'POST':
        print(request.POST)
    return render (request, 'quiz/test_2.html', {'form':quizz, 'creator': 'creator'})
 {% for item in quiz|slice:':1'  %}
      <h2 class="blog-post-title">{{item.quiz_name.name}}</h2>
      <p class="blog-post-meta">{{item.quiz_name.created}} by <a href="#">{{ item.quiz_name.creator }}</a>       
      </p>
      </article>
      <h5> Pass mark is {{item.quiz_name.pass_mark }}. You Scored: </h5>
      <h5 class="d-none inline-block" id="score"></h5>
      <p class="text-wrap">
        {{ item.quiz_name.description|safe }}
      </p>
      {{ break }}
    {% endfor %}
