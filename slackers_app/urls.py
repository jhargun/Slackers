from django.urls import path
from . import views

app_name='slackers_app'
urlpatterns = [
    path('', views.index, name="index"),
    path('make', views.make, name="make"),
    path('home', views.home, name='home'),
    path('edit', views.edit, name='edit'),
]
