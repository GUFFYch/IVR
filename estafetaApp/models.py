from pydoc_data.topics import topics
import uuid
from django.db import models
from django.forms import ModelForm


# Create your models here.
class Tests(models.Model):
    name = models.CharField(max_length=100, unique=True)  # название
    subject = models.CharField(max_length=100) # темы
    level = models.CharField(max_length=50) # для каких уровней
    description = models.CharField(max_length=500) # ссылка на контест
    is_active = models.BooleanField(default=True) # Окончен или нет
    game_mode = models.CharField(max_length=100) # режим игры
    question_amount = models.IntegerField() # кол-во вопросов
    test_time = models.CharField(max_length=10000)# время на вопрсо
    max_score = models.IntegerField() # всего баллов
    # статистика по ответам
    users_passed = models.CharField(max_length=1000000)
    teams_passed = models.CharField(max_length=1000000)
    teams_mark = models.CharField(max_length=1000000)
    users_answers = models.CharField(max_length=1000000)

class Questions(models.Model):
    test_name = models.CharField(max_length=10000) # текст вопроса
    question_amount = models.IntegerField() # кол-во вопросов
    test_text = models.CharField(max_length=10000) # текст вопроса
    test_answer = models.CharField(max_length=10000) # овтет на вопрос
    test_score = models.CharField(max_length=10000) # кол-во баллов за тест

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True) # название
    password = models.CharField(max_length=100) # пароль
    players_amount = models.IntegerField() # кол-во игроков
    games_played = models.IntegerField() # сыграно игр
    wins = models.IntegerField() # победы
    loses = models.IntegerField() # проигрыши
