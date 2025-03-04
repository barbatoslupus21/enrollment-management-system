from django.contrib import admin
from .models import SubjectList, Course, SubjectSection, SectionStudents, ProfessorSchedule, EnrollmentConfirmation, EnrollmentProgress, Event

admin.site.register(SubjectList)
admin.site.register(Course)
admin.site.register(SubjectSection)
admin.site.register(SectionStudents)
admin.site.register(ProfessorSchedule)
admin.site.register(EnrollmentConfirmation)
admin.site.register(EnrollmentProgress)
admin.site.register(Event)
