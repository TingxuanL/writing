from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http.response import HttpResponseNotFound, HttpResponseBadRequest
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.utils.translation import gettext as _

import json
import random

from .models import WritingExam, WritingRecord, WritingAssignment, TeacherStudentRelation
from .extract_features import extract_features


@login_required
def index(request):
    return HttpResponseRedirect(reverse('writing:exam'))


def error_message_view(request, message):
    auth.logout(request)
    context = {
        'message': message,
    }
    return render(request, 'writing/error_message.html', context)

@login_required
def exam(request):
    assignment = WritingAssignment.objects.filter(student=request.user).first()
    if not assignment:
        return error_message_view(request, _("您还未被分配考试！"))

    if assignment.access_time:
        return error_message_view(request, _("请勿重复进入考试!"))

    exam = assignment.exam
    writing_record = WritingRecord.objects.filter(user=request.user, exam=exam)
    if writing_record:
        return error_message_view(request, _("您已参加过考试，请勿重复参加！"))

    assignment.access_time = timezone.now()
    assignment.save()
    context = {
        'record': True,
        'exam': exam,
        'username': request.user.first_name or request.user.username,
    }
    return render(request, 'writing/exam.html', context)

def thank_you(request):
    return error_message_view(request, _('感谢您的参与！'))

@login_required
@require_POST
def record_exam(request, exam_id):
    exam = get_object_or_404(WritingExam, pk=exam_id)
    writing_record = WritingRecord.objects.filter(user=request.user, exam=exam).first()
    if writing_record:
        return error_message_view(request, _("您已参加过考试，请勿重复参加！"))
    record = request.POST['examRecord']
    article = request.POST['EnglishWriting']
    writing_record = WritingRecord(user=request.user, exam=exam, article=article, record=record, datetime=timezone.now())
    writing_record.save()
    return HttpResponseRedirect(reverse('writing:thank_you'))


@login_required
def replay_exam(request, exam_id):
    # NOTE: we only show one record
    exam = get_object_or_404(WritingExam, pk=exam_id)
    writing_record = WritingRecord.objects.filter(user=request.user, exam=exam).first()
    if not writing_record:
        return error_message_view(request, _("您还未参加过本考试"))
    context = {
        'record': False,
        'exam': exam,
        'writing_record': writing_record,
        'username': request.user.first_name or request.user.username,
    }
    return render(request, 'writing/exam.html', context)


@login_required
def replay_user_exam(request, user_id, exam_id):
    # NOTE: we only show one record
    exam = get_object_or_404(WritingExam, pk=exam_id)
    user = get_object_or_404(User, pk=user_id)
    writing_record = WritingRecord.objects.filter(user=user, exam=exam).first()
    if not writing_record:
        return HttpResponse(_("该用户还未参加过考试！"))
    context = {
        'record': False,
        'exam': exam,
        'writing_record': writing_record,
        'username': user.first_name or user.username,
    }
    return render(request, 'writing/exam.html', context)


@login_required
def dashboard(request):
    if request.user.groups.filter(name='Writing Admin').exists():
        teachers = User.objects.filter(groups__name='Teacher').order_by('username')
    else:
        teachers = []
    if request.user.groups.filter(name='Teacher').exists():
        students = request.user.my_students.all()
    else:
        students = []
    context = {
        'teachers': teachers,
        'students': students,
    }
    return render(request, 'writing/dashboard/home.html', context)


@login_required
def extract_features_view(request):
    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest(_('Permission denied'))

    context = {}
    return render(request, 'writing/dashboard/download_data.html', context)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required
@require_POST
def extract_features_ajax(request):
    if not is_ajax(request):
        return HttpResponseBadRequest('Expecting Ajax call')

    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')

    cnt_extracted = 0
    for i, writing_record in enumerate(WritingRecord.objects.all()):
        if writing_record.user.username.startswith('litest'):
            continue
        try:
            features = extract_features(writing_record)
        except:
            print('Extraction error', i, writing_record)
        else:
            writing_record.features = json.dumps(features)
            writing_record.save()
            cnt_extracted += 1

    success = True
    json_errors = {}
    json_return = {
        'success': success,
        'errors': json_errors,
        'cnt_extracted': cnt_extracted,
    }
    return JsonResponse(json_return)


@login_required
def download_features(request):
    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')

    json_res = {}
    for writing_record in WritingRecord.objects.all():
        if writing_record.features:
            json_res[writing_record.user.username] = json.loads(writing_record.features)

    json_res = json.dumps(json_res)
    resp = HttpResponse(json_res, content_type='application/text;charset=UTF-8')
    resp['Content-Disposition'] = 'attachment; filename=extracted_features.txt'

    return resp


@login_required
def create_student(request):
    if not (request.user.groups.filter(name='Writing Admin').exists() or 
        request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')

    if request.user.groups.filter(name='Writing Admin').exists():
        teachers = User.objects.filter(groups__name='Teacher').order_by('username')
    else:
        teachers = []
    context = {
        'teachers': teachers,
    }
    return render(request, 'writing/dashboard/create_student.html', context)


@login_required
@require_POST
def create_student_ajax(request):
    if not is_ajax(request):
        return HttpResponseBadRequest('Expecting Ajax call')

    success = True
    json_errors = {}
    teacher = None
    has_permission = False

    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')
    else:
        has_permission = True
        teacher_id = request.POST.get('inputTeacherID', '')
        # print('get teacher id', teacher_id)
        if not teacher_id or teacher_id == 'none':
            success = False
            json_errors['message'] = 'Wrong Teacher ID'
        else:
            teacher = User.objects.get(pk=teacher_id)
    
    if not (has_permission or request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')
    else:
        if not has_permission:
            if teacher is None:
                teacher = request.user
                success = True
                json_errors['message'] = ''

    cnt_created = 0
    if teacher is not None:
        # print('got teacher', teacher)
        student_ids = request.POST.get('TextareaStudentIDs', '')
        student_ids = student_ids.split()
        for sid in student_ids:
            sid = sid.strip()
            if sid:
                sname = f'{teacher.username}_{sid}'
                student = User.objects.filter(username=sname).first()
                if not student:
                    student = User.objects.create_user(sname, password=str(sid), first_name=str(sid))
                    cnt_created += 1
                    try:
                        student.teacherstudentrelation
                    except User.teacherstudentrelation.RelatedObjectDoesNotExist:
                        teacher.my_students.create(student=student)

    json_return = {
        'success': success,
        'errors': json_errors,
        'cnt_created': cnt_created,
    }
    return JsonResponse(json_return)


@login_required
def create_teacher(request):
    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')
    context = {}
    return render(request, 'writing/dashboard/create_teacher.html', context)


@login_required
@require_POST
def create_teacher_ajax(request):
    if not is_ajax(request):
        return HttpResponseBadRequest('Expecting Ajax call')

    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')

    success = True
    json_errors = {}

    cnt_created = 0
    # print('got teacher', teacher)
    student_ids = request.POST.get('TextareaStudentIDs', '')
    student_ids = student_ids.split()
    teacher_group = Group.objects.get(name='Teacher')
    for sid in student_ids:
        sid = sid.strip()
        if sid:
            sname = sid
            student = User.objects.filter(username=sname).first()
            if not student:
                student = User.objects.create_user(sname, password=str(sid))
                student.groups.add(teacher_group)
                student.save()
                cnt_created += 1

    json_return = {
        'success': success,
        'errors': json_errors,
        'cnt_created': cnt_created,
    }
    return JsonResponse(json_return)


@login_required
def create_exam(request):
    if not (request.user.groups.filter(name='Writing Admin').exists() or 
        request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')

    context = {}
    return render(request, 'writing/dashboard/create_exam.html', context)


@login_required
@require_POST
def create_exam_ajax(request):
    if not is_ajax(request):
        return HttpResponseBadRequest('Expecting Ajax call')

    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')

    success = True
    json_errors = {}

    exam_discription = request.POST.get('TextareaExamDiscription', '')
    if not exam_discription:
        success = False
        json_errors['message'] = 'Discription should not be empty!'
    else:
        json_errors['message'] = ''

    exam_title = request.POST.get('ExamTitle', '')
    if not exam_title:
        success = False
        json_errors['message'] += 'Title should not be empty!'
    
    exam_time = request.POST.get('ExamTime', '')
    if not exam_time:
        success = False
        json_errors['message'] += 'Time should not be empty!'
    else:
        exam_time = int(exam_time)
    
    if success:
        WritingExam.objects.create(title=exam_title, description=exam_discription, time=exam_time)

    json_return = {
        'success': success,
        'errors': json_errors,
    }
    return JsonResponse(json_return)


@login_required
def edit_exam(request, exam_id):
    if not (request.user.groups.filter(name='Writing Admin').exists() or 
        request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')

    exam = get_object_or_404(WritingExam, pk=exam_id)
    context = {
        'exam': exam,
    }
    return render(request, 'writing/dashboard/edit_exam.html', context)


@login_required
@require_POST
def edit_exam_ajax(request, exam_id):
    if not is_ajax(request):
        return HttpResponseBadRequest('Expecting Ajax call')

    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')

    success = True
    json_errors = {}

    exam_discription = request.POST.get('TextareaExamDiscription', '')
    if not exam_discription:
        success = False
        json_errors['message'] = 'Discription should not be empty!'
    else:
        json_errors['message'] = ''

    exam_title = request.POST.get('ExamTitle', '')
    if not exam_title:
        success = False
        json_errors['message'] += 'Title should not be empty!'
    
    exam_time = request.POST.get('ExamTime', '')
    if not exam_time:
        success = False
        json_errors['message'] += 'Time should not be empty!'
    else:
        exam_time = int(exam_time)
    
    if success:
        try:
            exam = WritingExam.objects.get(pk=exam_id)
        except WritingExam.DoesNotExist:
            success = False
            json_errors['message'] += 'This exam does not exist!'
        else:
            exam.title = exam_title
            exam.description = exam_discription
            exam.time = exam_time
            exam.save()

    json_return = {
        'success': success,
        'errors': json_errors,
    }
    return JsonResponse(json_return)


@login_required
def exam_list(request):
    if not (request.user.groups.filter(name='Writing Admin').exists() or 
        request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')
    
    exams = WritingExam.objects.all()
    context = {
        'exams': exams,
    }
    return render(request, 'writing/dashboard/exam_list.html', context)


@login_required
def exam_record_list(request):
    if not (request.user.groups.filter(name='Writing Admin').exists() or 
        request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')

    if request.user.groups.filter(name='Writing Admin').exists():
        teachers = User.objects.filter(groups__name='Teacher').order_by('username')
        students = []
        for teacher in teachers:
            students.extend(sorted([x.student for x in teacher.my_students.all()], key=lambda x: x.username))
    else:
        if request.user.groups.filter(name='Teacher').exists():
            teacher = request.user
            students = [x.student for x in teacher.my_students.all()]
            students.sort(key=lambda x: x.username)
        else:
            return HttpResponseBadRequest('Permission denied')

    # NOTE: this one should be careful, because there might be multiple 
    # records for one student on one exam,
    # although we try to prevent this in the view.py
    exam_records = []
    exams = []
    for student in students:
        try:
            exam = student.writingassignment.exam
        except User.writingassignment.RelatedObjectDoesNotExist:
            exam = None
        exams.append(exam)
        if exam is not None:
            exam_records.append(WritingRecord.objects.filter(user=student, exam=exam).first())
        else:
            exam_records.append(None)

    context = {
        'exam_records': zip(students, exams, exam_records),
    }
    return render(request, 'writing/dashboard/exam_record_list.html', context)


@login_required
def grade_exam_record(request, record_id):
    if not (request.user.groups.filter(name='Writing Admin').exists() or 
        request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')
    
    record = get_object_or_404(WritingRecord, pk=record_id)
    context = {
        'record': record,
    }
    return render(request, 'writing/dashboard/grade_exam_record.html', context)


@login_required
@require_POST
def grade_exam_record_ajax(request, record_id):
    if not is_ajax(request):
        return HttpResponseBadRequest('Expecting Ajax call')

    if not (request.user.groups.filter(name='Writing Admin').exists() or 
        request.user.groups.filter(name='Teacher').exists()):
        return HttpResponseBadRequest('Permission denied')

    success = True
    json_errors = {}
    
    exam_score = request.POST.get('ExamScore', '')
    if not exam_score:
        success = False
        json_errors['message'] = 'Score should not be empty!'
    else:
        exam_score = int(exam_score)
    
    if success:
        record = get_object_or_404(WritingRecord, pk=record_id)
        record.score = exam_score
        record.save()

    json_return = {
        'success': success,
        'errors': json_errors,
    }
    return JsonResponse(json_return)


@login_required
def assign_exam(request):
    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')

    context = {}
    return render(request, 'writing/dashboard/assign_exam.html', context)


@login_required
@require_POST
def assign_exam_ajax(request):
    if not is_ajax(request):
        return HttpResponseBadRequest('Expecting Ajax call')

    if not request.user.groups.filter(name='Writing Admin').exists():
        return HttpResponseBadRequest('Permission denied')

    teachers = User.objects.filter(groups__name='Teacher').order_by('username')
    students = []
    for teacher in teachers:
        students.extend(sorted([x.student for x in teacher.my_students.all()], key=lambda x: x.username))
    cnt_newly_assigned = 0
    all_exams = list(WritingExam.objects.all())
    for student in students:
        try:
            exam_assignment = student.writingassignment
        except User.writingassignment.RelatedObjectDoesNotExist:
            cnt_newly_assigned += 1
            exam = random.choice(all_exams)
            WritingAssignment.objects.create(student=student, exam=exam)

    success = True
    json_errors = {}
    json_return = {
        'success': success,
        'errors': json_errors,
        'cnt_newly_assigned': cnt_newly_assigned,
        'cnt_assigned': len(students),
    }
    return JsonResponse(json_return)