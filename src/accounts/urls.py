#!/usr/bin/env python
# coding=utf-8
from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    # ex: /
    path(r'login/', views.login_view, name='login_view'),
    path(r'logout/', views.logout_view, name='logout_view'),
]
