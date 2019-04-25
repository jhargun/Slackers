from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'slackers_templates/homepage.html', {"form":login_form})

# Create your views here.
