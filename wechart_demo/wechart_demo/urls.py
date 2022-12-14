"""wechart_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from . import views,petdb

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
    path('adduser/', petdb.adduser),
    path('adddict/', petdb.adddict),
    path('addfriend/', petdb.addfriend),
    path('adddictcomment/', petdb.adddictcomment),
    path('addpet/', petdb.addpet),
    path('changepetstatus/', petdb.changepetstatus),
    path('changedictstatus/', petdb.changedictstatus),
    path('changedictcommentstatus/', petdb.changedictcommentstatus),
    path('login/', petdb.login),
    path('getdict/', petdb.getdict),
    path('getdictcomment/', petdb.getdictcomment),
    path('getfriend/', petdb.getfriend),
    path('getpetstatus/', petdb.getpetstatus),
    path('getuserinfo/', petdb.getuserinfo),
    path('addpetinfo/', petdb.addpetinfo),
    path('getpetinfo/', petdb.getpetinfo),
]
