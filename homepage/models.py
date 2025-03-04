from django.db import models
from django.contrib.auth.models import AbstractUser

class System_users(AbstractUser):
    USERROLE_TYPES = {
        'Student':'Student',
        'Professor':'Professor',
        'Administrator':'Administrator'
    }
    avatar = models.ImageField(upload_to='profile-avatar/', null=True, default='avatar.png') 
    id_number = models.CharField(max_length=50, null=True)
    firstName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    contact = models.IntegerField(null=True)
    email = models.EmailField(unique=True, null=True)
    username = models.CharField(max_length=50, null=True, unique=True)
    userrole = models.CharField(max_length=20, choices=USERROLE_TYPES, default="Student")
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    new_user = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


class UserInformation(models.Model):
    SEMESTERS={
        '1st Semester':'1st Semester',
        '2nd Semester':'2nd Semester',
        '3rd Semester':'3rd Semester',
        '4th Semester':'4th Semester',
        '5th Semester':'5th Semester'
    }

    user = models.OneToOneField(System_users, on_delete=models.CASCADE, null=True, related_name="student_info")
    year_level = models.IntegerField(null=True)
    course = models.ForeignKey('administrator.Course', on_delete=models.CASCADE, null=True)
    semester = models.CharField(max_length=100, choices=SEMESTERS, null=True)
    enrolled = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.userrole} - {self.user.id_number} - {self.user.name}"
    

class Professor(models.Model):
    user = models.OneToOneField(System_users, on_delete=models.CASCADE, null=True, related_name="prof_info")
    name_ext = models.CharField(max_length=50, default="Prof.")
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100) 
    hire_date = models.DateField(null=True)
    
    def __str__(self):
        return f"{self.user.userrole} - {self.user.id_number} - {self.user.name}"