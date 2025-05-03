from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
# Create your views here.

'''
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Autenticaciòn exitosa')
                else:
                    return HttpResponse('Cuenta desactivada')
            else:
                return HttpResponse('Credenciales incorrectas')
    else:
        form = LoginForm()
    return render(request, 'servidores/login.html', {'form': form})
'''

@login_required
def dashboard(request):
    return render(request,
                  'servidores/dashboard.html',
                  {'section': 'dashboard'})
