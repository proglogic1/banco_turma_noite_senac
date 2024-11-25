from django.urls import path
from .views import login_view,logout_view
from two_factor.urls import urlpatterns as tf_urls
from django.urls import include


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/',logout_view, name='logout'),
    

    path('', include(tf_urls)),


]
