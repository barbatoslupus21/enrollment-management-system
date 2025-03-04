from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.user_accounts, name="account"),
    path('confirm/<str:pk>/', views.confirm_account, name="confirm-account"),
    path('deactivate/<str:pk>/', views.deactivate_account, name="deactivate-account"),

    # Schedule
    path('schedule/', views.schedule_view, name='schedule'),
    path('create-subject/', views.create_subject, name='create-subject'),
    path('close-subject/<int:pk>/', views.close_subject, name='close-subject'),
    path('edi-subject/<int:pk>/', views.edit_subject, name='edit-subject'),
    path('get-open-subjects/<int:course_id>/', views.get_open_subjects, name='get_open_subjects'),
    path('get_professor_schedule/', views.get_professor_schedule, name='get_professor_schedule'),
    path('new-section/', views.new_section, name="new-section"),
    path('check-all-professor-conflicts/', views.check_all_professor_conflicts, name='check_all_professor_conflicts'),

    # Confirmation
    path('enrollment/', views.confirmations_view, name='enrollment'),
    path('approval/<int:pk>/', views.confirm_registration, name='approval'),
    path('tagged-subjects/', views.tagged_confirmation, name="tagged"),
    path('remove-tag/<int:pk>/', views.remove_tag, name='remove-tag'),

    # Professor's Account
    path('professors/', views.professors_accounts, name='professor'),
    path('enrolled?/<int:pk>/', views.confirm_subjects, name="confirm-tagging"),

    # Overview
    path('overview/', views.admin_overview, name='admin-overview'),

    # API
    path('api/enrollment-chart/', views.enrollment_chart_data, name='enrollment-chart'),
    path('api/student-statistics/', views.student_statistics, name='student-statistics'),
]
