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
import math

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
            content['team_members'] = [i for i in Account.objects.filter(team=user.team)]
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

def infoTest_page(request, name):
    content = {}
    test = Tests.objects.get(name=name)
    quest = Questions.objects.get(test_name=name)
    users_indexes = list(filter(None, test.users_passed.split(' | ')))
    users = [Account.objects.get(id=i).first_name for i in users_indexes]
    answers_arr = list(filter(None, test.users_answers.split(' | ')))
    scores_arr = list(filter(None, test.users_marks.split(' | ')))
    print(scores_arr, test.max_score)
    question_amount = quest.question_amount
    question_answers = list(filter(None, quest.test_answer.split(",")))
    content['test'] = test
    content['questions'] = [i+1 for i in range(quest.question_amount)]
    content['users'] = [{
        'user':users[i],
        'answers': [i for i in answers_arr[question_amount*i:question_amount*(i+1)]],
        'question_amount':quest.question_amount,
        'question_answers':question_answers,
        'max_score':test.max_score,
        'user_score':scores_arr[i],
        'user_correction':math.ceil(int(scores_arr[i]) * 100 / int(quest.question_amount)),
    } for i in range(len(users_indexes))]
    # print(content['tests'])
    return render(request, 'outpLists/showstatics.html', content)
def removeTest_page(request, name):
    Questions.objects.get(test_name=name).delete()
    Tests.objects.get(name=name).delete()
    return HttpResponseRedirect('/finishtest/')

# func to create test
def createtest_page(request):
    if request.user.is_authenticated:
        if request.method == 'POST' and 'submitBtn' in request.POST:
            test_text = ''
            test_answer = ''
            test_score = ''
            max_score = 0
            amount = 0
            for i in range(int(request.POST['amount'])):
                amount += i
                test_text += str(request.POST[f'question_{i}_text']) + ','
                test_answer += str(request.POST[f'question_{i}_ans']) + ','
                test_score += str(request.POST[f'question_{i}_score']) + ','
                max_score += int(request.POST[f'question_{i}_score'])
           
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
            question.question_amount = int(request.POST['amount'])
            test.question_amount = int(request.POST['amount'])
            test.max_score = max_score
            question.save()
            test.save()
            return HttpResponseRedirect('/createtest/')
        return render(request, 'createtest.html')
    return render(request, 'notadmin.html')
# test page function
def test_apge(request, name):
    test = Tests.objects.get(name=name)
    quest = Questions.objects.get(test_name=name)
    gamemode = int(test.game_mode)
    if test.game_mode in ['3', '4'] and request.user.team == '':
        return HttpResponseRedirect('/')
    if str(request.user.id) in test.users_passed.split(' | '):
        return HttpResponseRedirect(f'/results/{name}')
    content = {}
    if request.user.is_authenticated:
        content['questions'] = [{
                                'test_text':list(filter(None,quest.test_text.split(",")))[i],
                                'test_score':int(list(filter(None,quest.test_score.split(",")))[i]),
                                'test_number': i+1,
                                } for i in range(quest.question_amount) ]    

        if request.method == 'POST' and 'saveAns':
            answers = test.users_answers
            teams_passed = list(filter(None, set(test.teams_passed.split(' | ') + [request.user.team])))
            teams_mark = test.teams_mark.split(' | ')
            score = 0
            for i in range(quest.question_amount):
                user_ans = request.POST[f'test_{i + 1}_answer'].strip()
                correction = 1 if user_ans == list(filter(None,quest.test_answer.split(",")))[i].strip() else 0
                answers += f'{user_ans}//{correction} | '
                score += int(list(filter(None,quest.test_score.split(",")))[i]) if correction else 0
            if test.game_mode in ['3', '4']:
                team_index = teams_passed.index(request.user.team)
                if teams_mark[team_index] == '':
                    teams_mark[team_index] = f'{score}'
                    test.teams_passed = ' | '.join(teams_passed)
                    test.teams_mark = ' | '.join(teams_mark)
                else:
                    teams_mark[team_index] = str(int(teams_mark[team_index]) +  score )
            test.users_passed += f'{request.user.id} | '
            test.users_answers = answers
            test.users_marks += f'{score} | '
            test.save()
            return HttpResponseRedirect(f'/results/{name}')

              
        return render(request, f'testpage_{gamemode%2}.html', content)
    else:
        return HttpResponseRedirect('/')
# function for showing resoults
def resultstest_page(request, name):
    content = {}
    test = Tests.objects.get(name=name)
    user_index = test.users_passed.split(' | ').index(f'{request.user.id}')
    quest = Questions.objects.get(test_name=name)
    answers_arr = test.users_answers.split('|')
    # arr with all Q&A of user
    content['questions'] = [{
                            'test_text':list(filter(None,quest.test_text.split(",")))[i],
                            'test_score':int(list(filter(None,quest.test_score.split(",")))[i]),
                            'test_number': i,
                            'user_answer': answers_arr[i + quest.question_amount*user_index].strip().split('//')[0],
                            'user_correction': answers_arr[i + quest.question_amount*user_index].strip().split('//')[-1],
                            'question_mark': int(list(filter(None,quest.test_score.split(",")))[i]) if answers_arr[i + quest.question_amount*user_index].strip().split('//')[0] == answers_arr[i + quest.question_amount*user_index].strip().split('//')[-1] else 0,
                            } for i  in range(quest.question_amount) ]
    
    # arr with marks of user
    content['mark'] = {
        'test_score':sum([int(list(filter(None,quest.test_score.split(",")))[i]) if answers_arr[i + quest.question_amount*user_index].strip().split('//')[0] == answers_arr[i + quest.question_amount*user_index].strip().split('//')[-1] else 0 for i in range(quest.question_amount)]), 
        'test_questions_amount': sum([int(list(filter(None,quest.test_score.split(",")))[i]) for i in range(quest.question_amount)]),
                }
    # checking if it was a team test to show team stats
    if test.game_mode in ['3', '4']:
        team_users = [i for i in list(filter(None,test.users_passed.split(' | '))) if Account.objects.get(id=i).team == request.user.team]
        indexes = [ test.users_passed.split(' | ').index(i) for i in team_users]
        # arr with team stats
        content['team'] = [{
            'first_name' : Account.objects.get(id=test.users_passed.split(' | ')[i]).first_name,
            'score' : sum([int(list(filter(None,quest.test_score.split(",")))[j]) if answers_arr[j + quest.question_amount*i].strip().split('//')[0] == answers_arr[j + quest.question_amount*i].strip().split('//')[-1] else 0 for j in range(quest.question_amount)]),
            'percentage': math.ceil(sum([int(list(filter(None,quest.test_score.split(",")))[j]) if answers_arr[j + quest.question_amount*i].strip().split('//')[0] == answers_arr[j + quest.question_amount*i].strip().split('//')[-1] else 0 for j in range(quest.question_amount)]) * 100 / sum([int(list(filter(None,quest.test_score.split(",")))[i]) for i in range(quest.question_amount)])),

        } for i in indexes]
    else:
        users = [i for i in list(filter(None,test.users_passed.split(' | ')))]
        indexes = [ test.users_passed.split(' | ').index(i) for i in users]
        # arr with team stats
        content['users_pass'] = [{
            'first_name' : Account.objects.get(id=test.users_passed.split(' | ')[i]).first_name,
            'score' : sum([int(list(filter(None,quest.test_score.split(",")))[j]) if answers_arr[j + quest.question_amount*i].strip().split('//')[0] == answers_arr[j + quest.question_amount*i].strip().split('//')[-1] else 0 for j in range(quest.question_amount)]),
            'percentage': math.ceil(sum([int(list(filter(None,quest.test_score.split(",")))[j]) if answers_arr[j + quest.question_amount*i].strip().split('//')[0] == answers_arr[j + quest.question_amount*i].strip().split('//')[-1] else 0 for j in range(quest.question_amount)]) * 100 / sum([int(list(filter(None,quest.test_score.split(",")))[i]) for i in range(quest.question_amount)])),

        } for i in indexes]
    content['test'] = test
    return render(request, 'resultpage.html', content)  

# function for deleting tests
def finishtest_page(request):
    if request.user.is_authenticated:
        
        return render(request, 'finishtest.html')
    return render(request, 'notadmin.html')

# main page function
def main_page(request):
    content = {}
    tests = Tests.objects.all()
    content['tests'] = [{
                'name':test.name,
                'subject':test.subject,
                'level':test.level,
                'description':test.description,
                'is_active':test.is_active,
                'game_mode':test.game_mode,
                'question_amount':test.question_amount,
                'max_score':test.max_score,
                'passed': 1 if str(request.user.id) in test.users_passed.split(' | ') else 0
            } for test in tests]
    
    
    return render(request, 'main.html', content)

# function for resoult page
def resultsall_page(request):
    if (request.user.is_authenticated):
        content = {}
        tests = Tests.objects.all()
        content['tests'] = [{
                'name':test.name,
                'subject':test.subject,
                'level':test.level,
                'description':test.description,
                'is_active':test.is_active,
                'game_mode':test.game_mode,
                'question_amount':test.question_amount,
                'max_score':test.max_score,
                'passed': 1 if str(request.user.id) in test.users_passed.split(' | ') else 0
            } for test in tests]        
        return render(request, 'results.html', content)
    else:
        return HttpResponseRedirect('/')

# logout default function
def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

# registration function
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

# login function
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
