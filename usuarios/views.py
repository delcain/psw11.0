from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth

def cadastro(request):
    if request.method == "GET":
        
        return render(request, 'cadastro.html')
    
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não são iguais.')
            print('Senhas são diferentes')
            return redirect(cadastro)
        
        if len(senha) < 5:
            messages.add_message(request, constants.ERROR, 'A senha deve ter no mínimo 5 caracteres.')
            print('Senha menor que 5 caracteres')
            return redirect(cadastro)
        
        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR, 'Esse nome de usuário não está disponível.')
            print('Usuário ja existe. Tente outro.')
            return redirect(cadastro)
        
        user = User.objects.create_user(
            username=username,
            password=senha
        )

        return redirect(logar)

    
def logar(request):
    if request.method == "GET":
        return render(request, 'logar.html')
    
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = auth.authenticate(request, username=username, password=senha)
        if user:
            auth.login(request, user)
            return HttpResponse("Logado")    
    
    messages.add_message(request, constants.ERROR, 'Usuário ou senha inválido.')
    return redirect(logar)

