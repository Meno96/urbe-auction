from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('sign-in', views.signInView, name='sign-in'),
    path('sign-up', views.signUpView, name='sign-up'),
    path('logout', views.logoutUser, name='logout'),
]