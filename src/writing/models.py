#!/usr/bin/env python
# coding=utf-8
from django.db import models
from django.utils.translation import gettext as _

from django.conf import settings

# Create your models here.

class WritingExam(models.Model):
    title = models.CharField(
        verbose_name=_('exam title'),
        help_text=_('Title. Do not exceed 255 characters.'),
        max_length=255
    )
    description = models.TextField(
        verbose_name=_('description')
    )
    time = models.IntegerField(
        verbose_name=_('minutes for this exam'),
        default=60
    )
    def __str__(self):
        return self.title

class WritingAssignment(models.Model):
    """ This only records ONE current assignment for a student.
    """
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('student'),
        on_delete=models.CASCADE,
        primary_key=True
    )
    exam = models.ForeignKey(
        WritingExam,
        verbose_name=_('exam'),
        on_delete=models.CASCADE
    )
    access_time = models.DateTimeField(
        verbose_name=_('first_access_time'),
        blank=True,
        null=True,
    )
    def __str__(self) -> str:
        return str(self.exam.title) + str(self.student)
        

class TeacherStudentRelation(models.Model):
    """ For one student, there is only one teacher.
    For one teacher, there are many students.
    """
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('teacher'),
        on_delete=models.CASCADE,
        related_name='my_students'
    )
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('student'),
        on_delete=models.CASCADE,
        primary_key=True
    )
    def __str__(self) -> str:
        return str(self.teacher) + str(self.student)
       

class WritingRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    exam = models.ForeignKey(
        WritingExam,
        verbose_name=_('exam'),
        on_delete=models.CASCADE
    )
    article = models.TextField(
        verbose_name=_('article')
    )
    record = models.TextField(
        verbose_name=_('record')
    )
    datetime = models.DateTimeField(
        verbose_name=_('datetime'),
    )
    features = models.TextField(
        verbose_name=_('features'),
        blank=True
    )
    score = models.IntegerField(
        verbose_name=_('score'),
        default=-1
    )

    def __str__(self) -> str:
        return str(self.exam.title) + str(self.user) + ' ' + str(self.datetime)
