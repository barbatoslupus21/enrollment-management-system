from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from .models import System_users


def homepage(request):
    return render(request, 'homepage/homepage.html')

def userlogin(request):
    if request.user.is_authenticated:
        if request.user.userrole == "Professor":
            if not hasattr(userLogin, 'prof_info'):
                return redirect('information')
            return redirect('professor-overview')
        elif request.user.userrole == "Administrator":
            return redirect('admin-overview')
        elif request.user.userrole == "Student":
            if not hasattr(userLogin, 'student_info'):
                return redirect('information')
            return redirect('student-overview')   
        else:
            messages.error(request, "Invalid user.")
            return redirect('homepage')

    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = System_users.objects.get(username=username)
        except System_users.DoesNotExist:
            messages.error(request, 'User does not exist.')
            context['login_modal'] = True
            return render(request, 'homepage/homepage.html', context) 

        userLogin = authenticate(request, username=username, password=password)

        if userLogin is not None:
            if userLogin.is_approved == False:
                messages.error(request, "Your registration is awaiting approval. Please monitor your school email for confirmation of account activation.")
                return redirect('homepage')
            else:
                login(request, userLogin)

                if userLogin.userrole == "Professor":
                    if not hasattr(userLogin, 'prof_info'):
                        return redirect('information')
                    return redirect('professor-overview')
                elif userLogin.userrole == "Administrator":
                    return redirect('admin-overview')
                elif userLogin.userrole == "Student":
                    if not hasattr(userLogin, 'student_info'):
                        return redirect('information')
                    return redirect('student-overview')        
                else:
                    messages.error(request, "Invalid user.")
                    return redirect('homepage')
        else:
            messages.error(request, "Login credentials are incorrect.")

    return redirect('homepage')

@login_required
def userlogout(request):
    logout(request)
    return redirect('homepage')

def register_user(request):
    if request.method == 'POST':
        idnumber = request.POST.get('idnumber')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        name=f'{firstname} {lastname}'
        contact = request.POST.get('contact-number')
        email = request.POST.get('email')
        userrole = request.POST.get('userrole')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            if System_users.objects.filter(username=idnumber).exists():
                messages.error(request, 'ID Number already exists!')
            elif System_users.objects.filter(id_number=idnumber).exists():
                messages.error(request, 'Id number already exists!')
            elif System_users.objects.filter(email=email).exists():
                messages.error(request, 'Email address already exists!')
            else:
                user = System_users.objects.create_user(id_number=idnumber, firstName=firstname, lastName=lastname, name=name, contact=contact, email=email, username=idnumber, userrole=userrole, password=password1)
                user.set_password(password1)
                user.save()
                messages.success(request, "Great, you've registered! Keep an eye on your school email for a notification that your account is approved and confirmed by the school.")
                return redirect('homepage')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('homepage')
    
    return redirect('homepage')
