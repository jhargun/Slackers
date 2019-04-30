from django.urls import path
from . import views

app_name='slackers_app'
urlpatterns = [
    path('', views.index, name="index"),
    path('make', views.make, name="make"),
    path('home', views.home, name='home'),
    path('home/<str:user_send>', views.user_page, name='send'),  # The str is the user who message is sent to
]
