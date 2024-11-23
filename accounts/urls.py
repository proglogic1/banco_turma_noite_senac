from django.urls import path
from .views import login_view,logout_view
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/',logout_view, name='logout'),
]
