"""estafeta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from estafetaApp import views
from django.conf.urls import include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logout_view),
    path('login/', views.login_page),
    path('signin/', views.reg_page, name='signup'),
    path('profile/', views.profile_page),
    path('quiz/<name>', views.test_apge),
    path('searchteam/<name>/', views.searchTeam_page),
    path('searchtest/<name>/', views.searchTest_page),
    # path('profile/<id>', views.profile_sertain_page),
    path('createtest/', views.createtest_page),
    path('finishtest/', views.finishtest_page),
    path('profile/<name>/', views.profileTemplate_page),
    path('table/', views.table_page),
    path('results/', views.resultsall_page),
    path('results/<id>', views.resultstest_page),
    path('results/info/', views.info_page),

]
