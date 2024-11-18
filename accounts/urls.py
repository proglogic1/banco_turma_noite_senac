from django.urls import path
from .views import login_view,cadastro,logout
#from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('cadastro/', cadastro , name ='cadastro' ),
    path('logout/', logout, name='logout'),
]
