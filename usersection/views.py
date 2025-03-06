from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import now
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse
from homepage.models import System_users, UserInformation, Professor
from notification.models import Notification
from administrator.models import SubjectList, Course, SubjectSection, ProfessorSchedule, EnrollmentConfirmation, SectionStudents, EnrollmentProgress, Event

# Students
@login_required
def student_enrollment(request):
    confirmation = EnrollmentConfirmation.objects.filter(student=request.user).last()
    progress = EnrollmentProgress.objects.filter(student=request.user).last()
    courses = Course.objects.all()
    if hasattr(request.user, 'student_info') and request.user.student_info and request.user.student_info.course:
        subjects = SubjectList.objects.filter(status=True, course=request.user.student_info.course).order_by('semester')
        user_subjects = SectionStudents.objects.filter(student=request.user).values_list('section__subject_id', flat=True).distinct()
        user_sections = SectionStudents.objects.filter(student=request.user).values_list('section_id', flat=True)
    else:
        subjects = SubjectList.objects.none()
        user_sections = []
        user_subjects = []

    tagged_subject = SectionStudents.objects.filter(student=request.user).count()
    context={
        'confirmation':confirmation,
        'courses':courses,
        'subjects':subjects,
        'progress':progress,
        'user_subjects':user_subjects,
        'user_sections': user_sections,
        'tagged_subject':tagged_subject
    }
    return render(request, 'usersection/student-enrollment.html', context)

@login_required
def register(request):
    student_info = get_object_or_404(UserInformation, user=request.user)
    if request.method == "POST":
        course = request.POST.get("regCourse")
        course_id = Course.objects.filter(id=course).first()
        semester = request.POST.get("regSemester")

        new_registration = EnrollmentConfirmation.objects.create(
            student = request.user
        )

        student_info.course=course_id
        student_info.semester=semester
        student_info.save()

        progress = EnrollmentProgress.objects.create(
            student=request.user
        )

        messages.success(request, 'Registration successfully submitted.')
        return redirect("student-enrollment")
    return redirect("student-enrollment")

@login_required
def join_section(request, pk):
    selected_section = get_object_or_404(SubjectSection, id=pk)
    if request.method == "POST":
        action = request.POST.get('action')
        if action == "add":
            section = SectionStudents.objects.create(
                section=selected_section,
                student=request.user
            )
            messages.success(request, f'Enrolled in section {selected_section.section}.')
        elif action == "remove":
            enrolled_section = get_object_or_404(SectionStudents, section=selected_section)
            enrolled_section.delete()
            messages.success(request, f'Leave in section {selected_section.section}')
        else:
            messages.success(request, 'Invalid action')
            return redirect(request.META.get("HTTP_REFERER", "/"))
    return redirect(request.META.get("HTTP_REFERER", "/"))

def get_enrollment_progress(request):
    progress = EnrollmentProgress.objects.filter(student=request.user).last()
    if progress:
        data = {
            "confirmation": progress.confirmation,
            "accounting": progress.accounting,
            "subject": progress.subject,
            "section": progress.section,
            "section_confirmation": progress.section_confirmation,
            "print_regform": progress.print_regform
        }
    else:
        data = {
            "confirmation": False,
            "accounting": False,
            "subject": False,
            "section": False,
            "section_confirmation": False,
            "print_regform": False
        }
    return JsonResponse(data)

@login_required
def finish_tagging(request):
    selected_progress = EnrollmentProgress.objects.filter(student=request.user).last()
    if request.method == "POST":
        selected_progress.subject=True
        selected_progress.section=True
        selected_progress.save()

        messages.success(request, 'Tagging completed.')
        return redirect("student-enrollment")
    return redirect("student-enrollment")

@login_required
def student_schedule(request):
    confirmation = EnrollmentConfirmation.objects.filter(student=request.user, schedule_confirmation=True).last()
    courses = Course.objects.all()
    subjects = SubjectList.objects.filter(status=True, course=request.user.student_info.course).order_by('semester')

    for enrolled in subjects:
        enrolled.is_enrolled= SectionStudents.objects.filter(section__subject=enrolled, student=request.user).first()

    context={
        'confirmation':confirmation,
        'courses':courses,
        'subjects':subjects,
        'enrolled':enrolled
    }
    return render(request, 'usersection/student-schedule.html', context)

@login_required
def information_form(request):
    courses = Course.objects.all()
    context={
        'courses':courses,
    }
    return render(request, 'usersection/user-information.html', context)

@login_required
def submit_info(request):
    account = get_object_or_404(System_users, id=request.user.id)

    if request.method == "POST":
        avatar = request.FILES.get('user-avatar')
        firstName = request.POST.get('firstname')
        lastName = request.POST.get('lastname')
        name=f"{firstName} {lastName}"
        email = request.POST.get('email')
        contact = request.POST.get('contact-number')
        course = request.POST.get('course')
        semester = request.POST.get('semester')
        level = request.POST.get('year-level')
        course_instance = Course.objects.filter(id=course).first()

        if System_users.objects.filter(email=email).exclude(id=account.id).exists():    
            messages.error(request, "This email is already in use by another account.")
            return redirect('information')

        info, created = UserInformation.objects.get_or_create(user=account)
        info.year_level = level
        info.course = course_instance
        info.semester = semester
        info.save()

        if avatar:
            account.avatar = avatar
        account.firstName = firstName
        account.lastName = lastName
        account.name = name
        account.email = email
        account.contact = contact
        account.save()

        messages.success(request, 'Your information has been successfully saved.')
        return redirect('information')

    return redirect('information')

@login_required
def student_overview(request):
    current_day = now().day

    if EnrollmentConfirmation.objects.filter(student=request.user, status='Approve').exists():
        subjectCount = SectionStudents.objects.filter(student=request.user).count()
    else:
        subjectCount = 0
    formatted_subjectCount = f"{subjectCount:04}"
    sections = SectionStudents.objects.filter(student=request.user)
    totalUnits = SubjectList.objects.filter(subject_section__in=sections.values_list('section', flat=True)).aggregate(Sum('units'))['units__sum'] or 0
    formatted_totalUnits = f"{totalUnits:04}"
    currentSubjects = SectionStudents.objects.filter(student=request.user,section__day=current_day).count()
    formatted_currentSubjects = f"{currentSubjects:04}"

    events = Event.objects.filter(course=request.user.student_info.course).all().order_by('-date_created')
    student_sections = SectionStudents.objects.filter(student=request.user,section__day=current_day)

    context={
        'subjectCount':formatted_subjectCount,
        'totalUnits':formatted_totalUnits,
        'events':events,
        'sections':student_sections,
        'currentSubjects':formatted_currentSubjects
    }
    return render(request, 'usersection/student-overview.html', context)

# Professor
@login_required
def professor_overview(request):
    current_day = now().day

    newsNotifs = Notification.objects.filter(reciever=request.user, module="prof-schedule").all().order_by('-send_at')
    subjectCount = SubjectSection.objects.filter(professor=request.user).count()
    formatted_subjectCount = f"{subjectCount:04}"
    sectionCounts = ProfessorSchedule.objects.filter(professor=request.user).count()
    formatted_sectionCounts = f"{sectionCounts:04}"
    currentCount = ProfessorSchedule.objects.filter(professor=request.user, section__day=current_day).count()
    formatted_currentCount = f"{currentCount:04}"
    current_sections = ProfessorSchedule.objects.filter(professor=request.user,section__day=current_day)

    context={
        'newsNotifs':newsNotifs,
        'subjectCount':formatted_subjectCount,
        'sectionCounts':formatted_sectionCounts,
        'currentCount':formatted_currentCount,
        'current_sections':current_sections
    }
    return render(request, 'usersection/professor-overview.html', context)

@login_required
def professor_schedule(request):
    subjects = SubjectList.objects.filter(subject_section__professor=request.user).all()
    courses = Course.objects.filter(subjectlist__subject_section__professor=request.user).distinct()
    
    context={
        'subjects':subjects,
        'courses':courses,
    }
    return render(request, 'usersection/professor-schedule.html', context)

@login_required
def submit_profInfo(request):
    account = get_object_or_404(System_users, id=request.user.id)

    if request.method == "POST":
        avatar = request.FILES.get('prof-avatar')
        firstName = request.POST.get('firstname')
        lastName = request.POST.get('lastname')
        name = f"{firstName} {lastName}"
        ext = request.POST.get('name-ext')
        department = request.POST.get('department')
        position = request.POST.get('position')
        hired_date_str = request.POST.get('hired-date')
        hired_date = datetime.strptime(hired_date_str, "%Y-%m-%d").date() if hired_date_str else None
        email = request.POST.get('email')
        contact_number = request.POST.get('contact-number')

        if System_users.objects.filter(email=email).exclude(id=account.id).exists():    
            messages.error(request, "This email is already in use by another account.")
            return redirect('information')

        info, created = Professor.objects.get_or_create(user=account)
        info.name_ext = ext
        info.department = department
        info.position = position
        info.hire_date = hired_date
        info.save()

        if avatar:
            account.avatar = avatar
        account.firstName = firstName
        account.lastName = lastName
        account.name = name
        account.email = email
        account.contact = contact_number
        account.save()

        messages.success(request, 'Your information has been successfully saved.')
        return redirect('information')

    return redirect('information')