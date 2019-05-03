from django.urls import path
from . import views

app_name = 'slackers_app'
urlpatterns = [
    path('', views.index, name="index"),
    path('make', views.make, name="make"),
    path('home', views.home, name='home'),
    path('edit', views.edit, name='edit'),
    path('change_chat/<str:chat_id>', views.switch_chat, name='c_edit'),
    path('chat_make', views.make_chat, name='c_make'),
    path('logout', views.logout, name='logout'),
]
