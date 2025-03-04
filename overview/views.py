from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate

# Student Overview
@login_required
def student_overview(request):
    context={}
    return render(request, 'overview/student_overview.html', context)

# Professional Overview
@login_required
def teacher_overview(request):
    context={}
    return render(request, 'overview/teacher_overview.html.html', context)

# Admin Overview
@login_required
def admin_overview(request):
    context={}
    return render(request, 'overview/admin_overview.html', context)
