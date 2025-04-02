from django.contrib import admin

from .models import WritingExam, WritingRecord, WritingAssignment, TeacherStudentRelation

admin.site.register(WritingExam)
admin.site.register(WritingRecord)
admin.site.register(WritingAssignment)
admin.site.register(TeacherStudentRelation)
