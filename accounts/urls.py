from django.urls import path
from .views import login
from . import views

urlpatterns = [
    path('login/', views.login, name='login')
]
