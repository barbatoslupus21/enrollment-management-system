from django.urls import path
from . import views

urlpatterns = [
    path('userinformation/', views.information_form, name="information"),
    path('submit-information/', views.submit_info, name='submit-info'),
    # Student
    path('student-enrollment/', views.student_enrollment, name='student-enrollment'),
    path('register/', views.register, name='register'),
    path('enroll/<int:pk>/', views.join_section, name='enroll-section'),
    path('get_enrollment_progress/', views.get_enrollment_progress),
    path('tagging/', views.finish_tagging, name='tagging'),
    path('schedule/', views.student_schedule, name='student-schedule'),
    path('student-overview/', views.student_overview, name='student-overview'),
    
    # Professor
    path('professor/', views.professor_overview, name='professor-overview'),
    path('professor-schedule/', views.professor_schedule, name='prof-schedule'),
    path('prof-info/', views.submit_profInfo, name="prof-info")
]
