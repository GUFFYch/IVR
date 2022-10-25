from cmath import phase
from itertools import count
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from account.models import Account
from django.core.files.storage import FileSystemStorage
import openpyxl
from .models import Tests, Team
from django.db.models import Q
import xlrd 
import csv
import pandas as pd

# table generator
def table_page(request):
    content = {}
    if request.user.is_authenticated:
        if request.FILES:
            excel_file = request.FILES["excel_file"]

            wb = openpyxl.load_workbook(excel_file)

            worksheet = wb["Sheet1"]
            print(worksheet)

            excel_data = list()

            for row in worksheet.iter_rows():
                row_data = list()
                for cell in row:
                    row_data.append(str(cell.value))
                excel_data.append(row_data)
            print(excel_data[1::])

            content["excel_data_start"] = excel_data[0]

            content["excel_data"] = excel_data[1::]

            return render(request, 'tables.html', content)
        else:
            return render(request, 'tables.html', content)
    else:
        return HttpResponseRedirect('/')

# func for showing 
def profile_page(request):
    content = {}
    if request.user.is_authenticated:
        email = request.user
        person = Account.objects.get(email=email)
        content['user'] = person
        if request.method == 'POST' and 'createTeam' in request.POST:
            try:
                team = Team()
                team.name = request.POST['name']
                team.password = request.POST['password']
                team.players_amount = request.POST['amount']
                team.games_played = 0
                team.wins = 0
                team.loses = 0
                team.save()
                person.team = request.POST['name']
                person.save()
                return HttpResponseRedirect('/profile/')
            except:
                print("error")
        if request.method == 'POST' and 'leaveTeam' in request.POST:
            person.team = ""
            person.save()
            return HttpResponseRedirect('/profile/')
        if request.method == 'POST' and 'joinTeam' in request.POST:
            team = Team.objects.get(name=request.POST['joinTeam'])
            if team.password == request.POST['password']:
                person.team = request.POST['joinTeam']
                person.save()
                return HttpResponseRedirect('/profile/')
            else:
                print("error")
            return HttpResponseRedirect('/profile/')    
        return render(request, 'profile.html', content)
    else:
        return render(request, 'notadmin.html')

# rendering template page of profile
def profileTemplate_page(request, name):
    content = {}
    if request.user.is_authenticated:
        path = f"profile/template{name}.html"
        user = Account.objects.get(email=request.user)
        if user.team:
            team = Team.objects.get(name=user.team)
            content['team'] = team
        else:
            content['team'] = ""
        return render(request, path, content)
    else:
        return HttpResponseRedirect('/singin')    

# func to outp all teams
def searchTeam_page(request, name):
    content = {}
    content['teams'] =  Team.objects.filter(name__icontains=name)
    return render(request, 'outpLists/teamslist.html', content)

# func to outp all tests
def searchTest_page(request, name):
    content = {}
    content['tests'] =  Tests.objects.filter(name__icontains=name)
    print(content['tests'])
    return render(request, 'outpLists/testslist.html', content)

# func to create test
def createtest_page(request):
    if request.user.is_authenticated:
        if request.method == 'POST' and 'submitBtn' in request.POST:
            test_text = ''
            test_answer = ''
            test_score = ''
            test_time = ''
            amount = 0
            for i in range(int(request.POST['amount'])):
                amount += i
                test_text += str(request.POST[f'question_{i}_text']) + ','
                test_answer += str(request.POST[f'question_{i}_ans']) + ','
                test_score += str(request.POST[f'question_{i}_score']) + ','
                test_time += str(request.POST[f'question_{i}_time']) + ','
           
            test = Tests()
            question = Questions()
            test.name = request.POST['name']
            test.description = request.POST['description']
            test.subject = request.POST['subject']
            test.level = request.POST['level']
            test.game_mode = request.POST['game_mode']
            question.question_amount = amount
            question.test_name = request.POST['name']
            question.test_text = test_text
            question.test_answer = test_answer
            question.test_score = test_score
            question.test_time = test_time
            question.question_amount = int(request.POST['amount'])
            test.question_amount = int(request.POST['amount'])
            test.max_score = 0
            question.save()
            test.save()
            return HttpResponseRedirect('/createtest/')
        return render(request, 'createtest.html')
    return render(request, 'notadmin.html')

def test_apge(request, name):
    content = {}
    if request.user.is_authenticated:
        test = Tests.objects.filter(name=name)
        quest = Questions.objects.filter(test_name=name)
        questions = []
        # print(questions[0].question_amount)
        # for i in range(0, quest[0].question_amount):
            # 'test_answer':quest[0].test_answer,
            # 'test_score':quest[0].test_score,
            # 'test_time':quest[0].test_time,
        
        content['questions'] = [{
                                    'test_text':list(filter(None,quest[0].test_text.split(",")))[i],
                                    'test_answer':list(filter(None,quest[0].test_answer.split(",")))[i],
                                    'test_score':int(list(filter(None,quest[0].test_score.split(",")))[i]),
                                    'test_time':int(list(filter(None,quest[0].test_time.split(",")))[i]),
                                    'test_number': i
                                } for i in range(quest[0].question_amount) ]    

        if request.method == 'POST' and 'saveAns':
            print(request.POST)
            return HttpResponseRedirect(f'/quiz/{name}')

              
        return render(request, 'testpage.html', content)
    else:
        return HttpResponseRedirect('/')


def finishtest_page(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            print(request.POST)

            test = Tests.objects.get(id = request.POST['testId'])
            test.is_active = False

            print(request.FILES)

            if request.FILES:
                print("---------------OK---------------")
                excel_file = request.FILES["excel_file"]

                wb = openpyxl.load_workbook(excel_file)

                worksheet = wb["Sheet1"]
                # print(worksheet)

                excel_data = list()

                for row in worksheet.iter_rows():
                    row_data = list()
                    for cell in row:
                        row_data.append(str(cell.value))
                    excel_data.append(row_data)


                url = str(test.id) + '.csv'
                test.results_link = url
                print(url)

            test.save()

            return HttpResponseRedirect('/finishtest/')
        return render(request, 'finishtest.html')
    return render(request, 'notadmin.html')

def main_page(request):
    content = {}
    tests = Tests.objects.all()
    content['tests'] = tests
    return render(request, 'main.html', content)

def resultsall_page(request):
    if (request.user.is_authenticated):
        content = {}
        tests = Tests.objects.all()
        content['tests'] = tests
        return render(request, 'results.html', content)
    else:
        return HttpResponseRedirect('/')

def resultstest_page(request, id):
    content = {}
    test = Tests.objects.get(id=id)
    content['test'] = test
 
    

    with open('2.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    print(data)


    content["excel_data_start"] = data[0]

    content["excel_data"] = data[1::]

    return render(request, 'resultTestPage.html', content)


def info_page(request):
    content = {}
    
    try:
        test = Tests.objects.get()
        user = Account.objects.get(email=request.user)
        content['user'] = user

        if request.FILES:

            # SAVE FILE TO CSV


            excel_file = request.FILES["excel_file"]

            wb = openpyxl.load_workbook(excel_file)

            worksheet = wb["Sheet1"]
            # print(worksheet)

            excel_data = list()

            for row in worksheet.iter_rows():
                row_data = list()
                for cell in row:
                    row_data.append(str(cell.value))
                excel_data.append(row_data)

            url = str(test.id) + '.csv'
            print(url)

            with open(url, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(excel_data)

            test['results_link'] = url

            print(test.id)


            # OPEN CSV FILE 


            with open(test['results_link'], newline='') as f:
                reader = csv.reader(f)
                data = list(reader)
            print(data)


            content["excel_data_start"] = data[0]

            content["excel_data"] = data[1::]

        return render(request, 'info.html', content)
    except:
        return render(request, 'info.html', content)

# def main_page(request):
#     content = {}
#     tests = Tests.objects.all()
#     content['tests'] = tests
#     return render(request, 'main.html', content)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

def reg_page(request):
    form = SignUpForm(request.POST)
    context = {
        'form': form
    }
    # вход

    if request.method == 'POST' and 'profile_saver3' in request.POST:
        # print(form.errors)
        # print(form.is_valid())
        list = request.POST.getlist('sports')

        print(list)


        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            password = form.cleaned_data.get('password1')

            phone = request.POST.get('phone')
            country = request.POST.get('country')
            subjects = request.POST.getlist('sports')
            knowledge = request.POST.get('knowledge')

            user = authenticate(email=email, password=password,
             first_name=first_name)

            user.phone = phone
            user.country = country
            user.knowledge = knowledge
            user.subjects = subjects
            print(request.POST)
            user.save()
            return redirect('/login/')

  

    return render(request, 'signin.html', context)

def login_page(request):

    if request.method == 'POST' and 'btnform2' in request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print('Try again! username or password is incorrect')
    return render(request, 'login.html')