from django.urls import path
from . import views

urlpatterns = [
    path('student-overview', views.student_overview, name='student-overview'),
    path('professor-overview', views.teacher_overview, name='teacher-overview'),
    path('admin-overview', views.admin_overview, name='admin-overview')
]
