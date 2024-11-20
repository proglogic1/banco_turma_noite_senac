from django.urls import path
from .views import login_view,logout
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', login_view, name='login'),
    #path('cadastro/', cadastro , name ='cadastro' ),
    path('logout/',auth_views.LogoutView.as_view(), name='logout'),
]
