from django.db import models
import random, string
from homepage.models import System_users

class Course(models.Model):
    course = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course

class SubjectList(models.Model):

    SEMESTERS={
        '1st Semester':'1st Semester',
        '2nd Semester':'2nd Semester',
        '3rd Semester':'3rd Semester',
        '4th Semester':'4th Semester',
        '5th Semester':'5th Semester'
    }

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=100, choices=SEMESTERS, null=True)
    course_code = models.CharField(max_length=50, null=True)
    course_title = models.CharField(max_length=100, null=True)
    units = models.IntegerField(null=True)
    laboratory = models.IntegerField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.course.course}: {self.semester}-{self.semester}'
    
class SubjectSection(models.Model):
    subject = models.ForeignKey(SubjectList, on_delete=models.CASCADE, related_name='subject_section')
    section = models.CharField(max_length=10, null=True, unique=True, blank=True)
    day = models.CharField(max_length=100, null=True)
    time_from = models.TimeField(null=True)
    time_to = models.TimeField(null=True)
    room = models.CharField(max_length=100, null=True)
    capacity = models.IntegerField(null=True)
    professor = models.ForeignKey(System_users, on_delete=models.SET_NULL, null=True, related_name='prof_sched')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.subject.course} - {self.section}: {self.professor.name}'
    
    def generate_unique_section(self):
        while True:
            section_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            if not SubjectSection.objects.filter(section=section_name).exists():
                return section_name

    def save(self, *args, **kwargs):
        if not self.section:
            self.section = self.generate_unique_section()
        super().save(*args, **kwargs)

class SectionStudents(models.Model):
    section = models.ForeignKey(SubjectSection, on_delete=models.CASCADE, related_name='student_section')
    student = models.ForeignKey(System_users, on_delete=models.CASCADE, related_name='user_section')
    date_tagged = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.section} : {self.student}'
    
class ProfessorSchedule(models.Model):
    professor = models.ForeignKey(System_users, on_delete=models.SET_NULL, null=True, related_name="prof_schedule")
    section = models.ForeignKey(SubjectSection, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.professor.name} - {self.section}'
    
class EnrollmentConfirmation(models.Model):
    STATUS={
        'Approve':'Approve',
        'Disapprove':'Disapprove',
        'Pending':'Pending'
    }
    student = models.ForeignKey(System_users, on_delete=models.CASCADE, related_name="student_enrollmentConfirmation")
    status= models.CharField(max_length=100, choices=STATUS, default='Pending')
    date_updated = models.DateTimeField(null=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    schedule_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return self.student.name
    
class EnrollmentProgress(models.Model):
    student = models.ForeignKey(System_users, on_delete=models.CASCADE, related_name='enrollment_progress')
    confirmation = models.BooleanField(default=False)
    accounting = models.BooleanField(default=False)
    subject = models.BooleanField(default=False)
    section = models.BooleanField(default=False)
    section_confirmation = models.BooleanField(default=False)
    print_regform = models.BooleanField(default=False)

    def __str__(self):
        return self.student.name
    
class Event(models.Model):
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.message