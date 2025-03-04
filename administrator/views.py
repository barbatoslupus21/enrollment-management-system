from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from homepage.models import System_users, UserInformation
from notification.models import Notification
from .models import SubjectList, Course, SubjectSection, ProfessorSchedule, EnrollmentConfirmation, EnrollmentProgress, SectionStudents, Event
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import EnrollmentStatsSerializer

@login_required
def user_accounts(request):
    users = System_users.objects.all().exclude(userrole="Administrator").order_by('is_approved')
    context={
        'accounts':users,
    }
    return render(request, 'administrator/account.html', context)

@login_required
def confirm_account(request, pk):
    selected_account = get_object_or_404(System_users, id=pk)

    if request.method == "POST":
        selected_account.is_approved = True
        selected_account.save()

        notif = Notification.objects.create(
            module="user-account",
            sender=request.user,
            reciever=selected_account,
            message="You're all set! Your account has been approved by the administrator."
        )

        subject = "Your Account is Approved! Welcome to the Enrollment Portal!"
        message = f"""Dear {selected_account.firstName},

Fantastic news!  We're thrilled to let you know that your account has been officially approved! Welcome to the Trimex Colleges Enrollment Portal!

You can now log in and start exploring all the great features and information available to you.  Get ready to dive in!

We're so excited to have you with us!  If you have any questions as you get started, don't hesitate to reach out.

Welcome aboard!

Sincerely,

Trimex Colleges
"""
        recipient_list = [selected_account.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

        messages.success(request, f'{selected_account.name} successfully approved.')
        return redirect('account')
    
    return redirect('account')

@login_required
def deactivate_account(request, pk):
    selected_account = get_object_or_404(System_users, id=pk)

    if request.method == "POST":
        selected_account.is_active = False
        selected_account.save()

        messages.success(request, f'{selected_account.name} has been deactivate.')
        return redirect('account')
    
    return redirect('account')


# Subjects
@login_required
def schedule_view(request):
    courses = Course.objects.all()
    subjects = SubjectList.objects.all()
    professors = System_users.objects.filter(userrole="Professor")
    context = {
        'subjects': subjects,
        'courses': courses,
        'professors': professors,
    }
    return render(request, 'administrator/schedule.html', context)

@login_required
def create_subject(request):
    if request.method == "POST":
        course = request.POST.get('course')
        semester = request.POST.get('semester')
        course_code = request.POST.get('course-code')
        course_title = request.POST.get('course-title')
        units = request.POST.get('unit')
        laboratory = request.POST.get('laboratory')

        try:
            course_id = Course.objects.filter(id=course).first()
        except SubjectList.DoesNotExist:
            messages.error(request, 'Error: Selected course does not exist.')
            return redirect('schedule')

        if SubjectList.objects.filter(course_code=course_code).exists():
            messages.error(request, 'Error: Course code already exists.')
            return redirect('schedule')

        if SubjectList.objects.filter(course_title=course_title).exists():
            messages.error(request, 'Error: Course title already exists.')
            return redirect('schedule')

        SubjectList.objects.create(
            course=course_id,
            semester=semester,
            course_code=course_code,
            course_title=course_title,
            units=units,
            laboratory=laboratory
        )

        messages.success(request, 'New subject created successfully.')
        return redirect('schedule')

    return redirect('schedule')

@login_required
def edit_subject(request, pk):
    selected_sub = get_object_or_404(SubjectList, id=pk)
    if request.method == "POST":
        course = request.POST.get('courseEdit')
        semester = request.POST.get('semesterEdit')
        course_code = request.POST.get('courseCodeEdit')
        course_title = request.POST.get('courseTitleEdit')
        units = request.POST.get('courseUnitsEdit')
        laboratory = request.POST.get('courseLaboratoryEdit')

        try:
            course_id = Course.objects.filter(id=course).first()
        except SubjectList.DoesNotExist:
            messages.error(request, 'Error: Selected course does not exist.')
            return redirect('schedule')

        selected_sub.course=course_id
        selected_sub.semester=semester
        selected_sub.course_code=course_code
        selected_sub.course_title=course_title
        selected_sub.units=units
        selected_sub.laboratory=laboratory
        selected_sub.save()

        messages.success(request, 'New subjects created')
        return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def close_subject(request, pk):
    selected_sub = get_object_or_404(SubjectList, id=pk)
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "open":
            selected_sub.status = True
            selected_sub.save()
            messages.success(request, f'{selected_sub.course_code}:{selected_sub.course_title} has been open.')
        elif action == "close":
            selected_sub.status = False
            selected_sub.save()
            messages.success(request, f'{selected_sub.course_code}:{selected_sub.course_title} has been closed.')
        else:
            messages.success(request, 'Invalid action')
            return redirect(request.META.get("HTTP_REFERER", "/"))

    return redirect(request.META.get("HTTP_REFERER", "/"))

def check_schedule_conflict(professor_id, day, time_from, time_to):
    if not all([professor_id, day, time_from, time_to]):
        return False

    try:
        time_from = datetime.strptime(time_from, '%H:%M').time()
        time_to = datetime.strptime(time_to, '%H:%M').time()
    except ValueError:
        return False

    conflicts = SubjectSection.objects.filter(
        professor_id=professor_id,
        day=day,  # Check the same day
        time_from__lt=time_to,
        time_to__gt=time_from
    ).exists()

    return conflicts

# Sections
@login_required
def new_section(request):
    if request.method == "POST":
        subject = request.POST.get('subject')
        subject_id = SubjectList.objects.filter(id=subject).first()
        day = request.POST.get('day')
        time_from = request.POST.get('start-time')
        time_to = request.POST.get('end-time')
        room = request.POST.get('room-name')
        capacity = request.POST.get('student-capacity')
        professor_id = request.POST.get('professor')
        professor_id_id = System_users.objects.filter(id=professor_id).first()

        if check_schedule_conflict(professor_id, day, time_from, time_to):
            messages.error(request, 'Schedule conflict detected. Please choose a different time or professor.')
            return redirect('schedule')
        else:
            new_section = SubjectSection.objects.create(
                subject=subject_id,
                day=day,
                time_from=time_from,
                time_to=time_to,
                room=room,
                capacity=capacity,
                professor_id=professor_id_id.id
            )

            new_schedule = ProfessorSchedule.objects.create(
                professor=professor_id_id,
                section=new_section
            )

            notif = Notification.objects.create(
                module="prof-schedule",
                sender=request.user,
                reciever=professor_id_id,
                message=f'You are now assigned to {subject_id.course_code}: {subject_id.course_title}.'
            )

            new_event = Event.objects.create(
                message=f'New section available: {subject_id.course_code}: {subject_id.course_title}',
                course=subject_id.course
            )

            subject = f"Class Assignment Notification - {subject_id.course_code}: {subject_id.course_title}"
            message = f"""Dear {professor_id_id.firstName},

This email is to inform you that you have been assigned to teach the following class:

    Course: {subject_id.course_code}: {subject_id.course_title}
    Schedule: {day} {time_from} - {time_to}
    Room: {room}

If you have any immediate questions, please do not hesitate to contact Trimex enrollment administrator.

Sincerely,

Trimex Colleges
"""
            recipient_list = [professor_id_id.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

        messages.success(request, 'New section has been created.')
        return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def get_open_subjects(request, course_id):
    open_subjects = SubjectList.objects.filter(
        course_id=course_id,
        status=True
    ).values('id', 'course_code', 'course_title', 'semester', 'units', 'laboratory')
    
    return JsonResponse({'subjects': list(open_subjects)})

@login_required
def get_professor_schedule(request):
    professor_id = request.GET.get('professor_id')
    schedules = ProfessorSchedule.objects.filter(professor_id=professor_id).select_related('section')
    
    data = []
    for schedule in schedules:
        section = schedule.section
        data.append({
            'subject': section.subject.course_title,
            'section': section.section,
            'day': section.day[:3],
            'time_from': section.time_from.strftime('%I:%M %p'),
            'time_to': section.time_to.strftime('%I:%M %p'), 
        })  
    
    return JsonResponse(data, safe=False)

def check_all_professor_conflicts(request):
    day = request.GET.get('day')
    time_from = request.GET.get('time_from')
    time_to = request.GET.get('time_to')
    
    if not all([day, time_from, time_to]):
        return JsonResponse({'conflicts': []})
    
    try:
        time_from_obj = datetime.strptime(time_from, '%H:%M').time()
        time_to_obj = datetime.strptime(time_to, '%H:%M').time()
    except ValueError:
        return JsonResponse({'conflicts': []})
    
    conflicting_schedules = SubjectSection.objects.filter(
        day=day,
        time_from__lt=time_to_obj,
        time_to__gt=time_from_obj
    )
    
    conflicting_professor_ids = conflicting_schedules.values_list('professor_id', flat=True).distinct()
    
    return JsonResponse({'conflicts': list(conflicting_professor_ids)})

# Confirmation
def confirmations_view(request):
    pendings = EnrollmentConfirmation.objects.filter(status="Pending")
    context={
        'pendings':pendings
    }
    
    return render(request, 'administrator/enrollment.html', context)

@login_required
def confirm_registration(request, pk):
    selected_reg = get_object_or_404(EnrollmentConfirmation, id=pk)
    student_progress = EnrollmentProgress.objects.filter(student=selected_reg.student).last()
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "approve":
            selected_reg.status = "Approve"
            selected_reg.save()

            notif = Notification.objects.create(
                module="student-enrollment",
                sender=request.user,
                reciever=selected_reg.student,
                message="Congratulations!. Your registration has been approved."
            )

            student_progress.confirmation=True
            student_progress.accounting=True
            student_progress.save()

            subject = "Application Update - Trimex Colleges"
            message = f"""Dear {selected_reg.student.firstName},

Great news! We're thrilled to let you know your registration has been approved! Welcome aboard!

You can now proceed to the enrollment portal to continue your enrollment journey and finalize your schedule.

We're excited to have you join our community!

Sincerely,

The Enrollment Team
Trimex Colleges
"""
            recipient_list = [selected_reg.student.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

            messages.success(request, f'{selected_reg.student.name} registration approved.')
        elif action == "disapprove":
            selected_reg.status = "Disapprove"
            selected_reg.save()

            notif = Notification.objects.create(
                module="student-enrollment",
                sender=request.user,
                reciever=selected_reg.student.email,
                message="We regret to inform you that your registration has been disapproved."
            )

            subject = "Application Update - Trimex Colleges"
            message = f"""Dear {selected_reg.student.firstName},

Thank you for your interest in enrolling at Trimex Colleges. We have carefully reviewed your registration application.

Unfortunately, we regret to inform you that we are unable to offer you a place at this time.

We appreciate you considering Trimex Colleges for your studies and wish you the best in your future endeavors.

Sincerely,

The Enrollment Team
Trimex Colleges
"""
            recipient_list = [selected_reg.student.email]
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

            messages.success(request, f'{selected_reg.student.name} registration disapproved.')
        else:
            messages.success(request, 'Invalid action')
            return redirect("enrollment")

    return redirect("enrollment")

# Professors
@login_required
def professors_accounts(request):
    professors = System_users.objects.filter(userrole="Professor")
    schedules = System_users.objects.filter(userrole="Professor").prefetch_related("prof_schedule")
    context = {
        'professors': professors,
        'schedules': schedules 
    }
    return render(request, 'administrator/professors.html', context)

# Tagged Subject
@login_required
def tagged_confirmation(request):
    unique_student_ids = SectionStudents.objects.values_list('student', flat=True).distinct()
    students = System_users.objects.filter(id__in=unique_student_ids).order_by('-date_joined').exclude(student_info__enrolled=True)

    section = None

    for student in students:
        student.tagged_subjects = SectionStudents.objects.filter(student=student)
        section = student.tagged_subjects

    context = {
        'students': students,
        'section': section
    }
    return render(request, 'administrator/registration-confirmation.html', context)

@login_required
def remove_tag(request, pk):
    selected_tag = get_object_or_404(SectionStudents, id=pk)

    if request.method == "POST":
        time_from = selected_tag.section.time_from
        time_to = selected_tag.section.time_to

        if timezone.is_naive(time_from):
            time_from = timezone.make_aware(time_from)
        if timezone.is_naive(time_to):
            time_to = timezone.make_aware(time_to)

        day = selected_tag.section.day[:3]  
        formatted_time_from = time_from.strftime("%I:%M %p") 
        formatted_time_to = time_to.strftime("%I:%M %p") 

        Notification.objects.create(
            module="student-schedule",
            sender=request.user,
            reciever=selected_tag.student,
            message=f"{selected_tag.section.subject.course_code}: {selected_tag.section.subject.course_title} with schedule {day} {formatted_time_from}-{formatted_time_to} has been removed from your schedule."
        )

        subject = f"Course Schedule Update - {selected_tag.section.subject.course_code}: {selected_tag.section.subject.course_title} Removed"
        message = f"""Dear {selected_tag.student.firstName},

Please be advised that the course {selected_tag.section.subject.course_code}: {selected_tag.section.subject.course_title}, originally scheduled for {day} from {formatted_time_from}-{formatted_time_to}, has been removed from your class schedule.

If you have any questions regarding this change, please do not hesitate to contact the enrollment office.

Sincerely,

The Enrollment Team
Trimex Colleges
    """
        recipient_list = [selected_tag.student.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        
        selected_tag.delete()
        messages.success(request, "Tagged subject has been removed.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def confirm_subjects(request, pk):
    selected_tag = EnrollmentConfirmation.objects.filter(student=pk, status="Approve").last()
    selected_progress = EnrollmentProgress.objects.filter(student=pk).last()
    selected_student = UserInformation.objects.get(user=pk)
    if request.method == "POST":
        selected_tag.schedule_confirmation=True
        selected_tag.date_updated=timezone.now()
        selected_progress.section_confirmation=True
        selected_student.enrolled=True
        selected_student.last_updated=timezone.now()
        selected_tag.save()
        selected_progress.save()
        selected_student.save()

        subject = "Subject Confirmed"
        message = f"""Dear {selected_student.user.firstName},

We're thrilled to inform you that your subject tagging has been successfully confirmed and approved!.

We're excited to have you with us! If you have any questions, please don't hesitate to contact the enrollment office.

Congratulations and welcome aboard!

Sincerely,

The Enrollment Team
Trimex Colleges
"""
        recipient_list = [selected_tag.student.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        
        messages.success(request, f'{selected_tag.student.name} successfully enrolled.')
        return redirect('enrollment')
    return redirect('enrollment')


# Overview
@login_required
def admin_overview(request):
    current_month = now().month
    current_year = now().year

    studentCount = System_users.objects.filter(userrole="Student", is_active=True).count()
    formatted_studentCount = f"{studentCount:04}"
    professorCount = System_users.objects.filter(userrole="Professor", is_active=True).count()
    formatted_professorCount = f"{professorCount:04}"
    classesCount = SubjectSection.objects.all().count()
    formatted_classesCount = f"{classesCount:04}"
    enrolledStudentCount = EnrollmentConfirmation.objects.filter(schedule_confirmation=True).count()
    formatted_enrolledStudentCount = f"{enrolledStudentCount:04}"
    classes = ProfessorSchedule.objects.all()
    enrolledStudents = EnrollmentConfirmation.objects.filter(schedule_confirmation=True, date_updated__year=current_year, date_updated__month=current_month).all().order_by('-date_updated')
    student_units = {}
    student_subjects = {}

    for enrollment in enrolledStudents:
        student = enrollment.student

        sections = SectionStudents.objects.filter(student=student)
        total_units = SubjectList.objects.filter(subject_section__in=sections.values_list('section', flat=True)).aggregate(Sum('units'))['units__sum'] or 0
        subject_count = SectionStudents.objects.filter(student=student).values('section__subject').distinct().count()
        student_subjects[student.id] = subject_count
        student_units[student.id] = total_units 

    context={
        'studentCount':formatted_studentCount,
        'professorCount':formatted_professorCount,
        'classesCount':formatted_classesCount,
        'enrolledStudentCount':formatted_enrolledStudentCount,
        'classes':classes,
        'enrolledStudents':enrolledStudents,
        'student_units':student_units,
        'student_subjects': student_subjects,
    }
    return render(request, 'administrator/overview.html', context)

@api_view(['GET'])
def enrollment_chart_data(request):
    data = EnrollmentStatsSerializer.get_monthly_enrollment_percentage()
    return Response(data)

@api_view(['GET'])
def student_statistics(request):
    total_students = System_users.objects.filter(userrole="Student").count()
    enrolled_students = UserInformation.objects.filter(user__userrole="Student", enrolled=True).count()

    return Response({
        "total_students": total_students,
        "enrolled_students": enrolled_students
    })