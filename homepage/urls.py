from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage, name='homepage'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.userlogout, name='logout'),
    path('register/', views.register_user, name='register-user'),
]
