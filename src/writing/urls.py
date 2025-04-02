#!/usr/bin/env python
# coding=utf-8
from django.urls import path

from . import views

app_name = 'writing'
urlpatterns = [
    # ex: /
    path('', views.index, name='index'),
    path('exam/', views.exam, name='exam'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('record/<int:exam_id>/', views.record_exam, name='record_exam'),
    path('replay/<int:exam_id>/', views.replay_exam, name='replay_exam'),
    path('replay/<int:user_id>/<int:exam_id>/', views.replay_user_exam, name='replay_user_exam'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/download-features/', views.download_features, name='download_features'),
    path('dashboard/create-student/', views.create_student, name='create_student'),
    path('dashboard/create-teacher/', views.create_teacher, name='create_teacher'),
    path('dashboard/create-exam/', views.create_exam, name='create_exam'),
    path('dashboard/edit-exam/<int:exam_id>/', views.edit_exam, name='edit_exam'),
    path('dashboard/exam-list/', views.exam_list, name='exam_list'),
    path('dashboard/exam-record-list/', views.exam_record_list, name='exam_record_list'),
    path('dashboard/grade-exam-record/<int:record_id>/', views.grade_exam_record, name='grade_exam_record'),
    path('dashboard/extract-features/', views.extract_features_view, name='extract_features_view'),
    path('dashboard/assign-exam/', views.assign_exam, name='assign_exam'),
    
    path('dashboard/ajax/extract-features/', views.extract_features_ajax, name='extract_features_ajax'),
    path('dashboard/ajax/create-student/', views.create_student_ajax, name='create_student_ajax'),
    path('dashboard/ajax/create-teacher/', views.create_teacher_ajax, name='create_teacher_ajax'),
    path('dashboard/ajax/create-exam/', views.create_exam_ajax, name='create_exam_ajax'),
    path('dashboard/ajax/edit-exam/<int:exam_id>/', views.edit_exam_ajax, name='edit_exam_ajax'),
    path('dashboard/ajax/assign-exam/', views.assign_exam_ajax, name='assign_exam_ajax'),
    path('dashboard/ajax/grade-exam-record/<int:record_id>/', views.grade_exam_record_ajax, name='grade_exam_record_ajax'),
]
