from django.shortcuts import redirect
from usuarios.views import logar

def index(request):
    return redirect(logar) 