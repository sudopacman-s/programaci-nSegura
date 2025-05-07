import subprocess
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario, Servidor, ContadorIntentos
from django.views.decorators.csrf import csrf_protect
import hashlib, paramiko, os
from django.conf import settings
from datetime import datetime
from datetime import timezone
from .utils import generar_captcha, validar_captcha
from django.http import HttpResponse
import random
import string
import requests
import time

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def exito(request) -> HttpResponse:
    """
    Página de éxito de demostración.

    request
    returns: HttpResponse 
    """
    return HttpResponse('Todo OK')

def ip_registrada(ip: str) -> bool:
    """
    True si la IP ya está en la BD.

    ip
    returns: bool 
    """
    try:
        ContadorIntentos.objects.get(pk=ip)
        return True
    except:
        return False
    

def fecha_en_ventana(fecha, segundos_ventana=settings.SEGUNDOS_INTENTO) -> bool:
    """
    True si la fecha está en la ventana de tiempo.

    fecha
    returns: bool 
    """
    actual = datetime.now(timezone.utc)
    diferencia = (actual - fecha).seconds
    return diferencia <= segundos_ventana
    
    


def tienes_intentos_login(request) -> bool:
    """
    Verdadero si puedes seguir intentando loguearte.

    request
    returns: bool 
    """
    ip = get_client_ip(request)
    if not ip_registrada(ip):
        registro = ContadorIntentos()
        registro.ip = ip
        registro.contador = 1
        registro.ultimo_intento = datetime.now(timezone.utc)
        registro.save()
        return True

    registro = ContadorIntentos.objects.get(pk=ip)
    fecha = registro.ultimo_intento
    if not fecha_en_ventana(fecha):
        registro.contador = 1
        registro.ultimo_intento = datetime.now(timezone.utc)
        registro.save()
        return True

    if registro.contador < settings.NUMERO_INTENTOS:
        registro.contador += 1
        registro.ultimo_intento = datetime.now(timezone.utc)
        registro.save()
        return True

    registro.ultimo_intento = datetime.now(timezone.utc)
    registro.save()
    return False
    
@csrf_protect
def login(request):
    if request.method == 'GET':
        a, b = generar_captcha(request)
        return render(request, 'login.html', {'captcha_a': a, 'captcha_b': b})

    usuario = request.POST.get('nombre_usuario', '').strip()
    contrasena = request.POST.get('contrasena', '').strip()
    respuesta = request.POST.get('captcha', '').strip()

    errores = []

    if not usuario or not contrasena:
        errores.append('Usuario y contraseña son obligatorios.')

    if not validar_captcha(request, respuesta):
        errores.append('Captcha incorrecto.')

    if errores:
        a, b = generar_captcha(request)
        return render(request, 'login.html', {
            'errores': errores,
            'captcha_a': a,
            'captcha_b': b,
            'usuario': usuario
        })

    hash_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()

    try:
        usuario_obj = Usuario.objects.get(nombre_usuario=usuario)
        if usuario_obj.contrasena_sha256 == hash_contrasena:
            if not usuario_obj.chat_id:
                errores.append('No tienes chat_id registrado.')
            else:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                expira = time.time() + settings.TIEMPO_TOKEN

                request.session['usuario_tmp'] = usuario
                request.session['token_2fa'] = token
                request.session['expira_2fa'] = expira

                enviar_token_telegram(usuario_obj.chat_id, token)
                return redirect('segundo_factor')
        else:
            errores.append('Credenciales incorrectas.')
    except Usuario.DoesNotExist:
        errores.append('No existe el usuario.')

    a, b = generar_captcha(request)
    return render(request, 'login.html', {
        'errores': errores,
        'captcha_a': a,
        'captcha_b': b,
        'usuario': usuario
    })

def enviar_token_telegram(chat_id, token):
    mensaje = f"Tu token de acceso es: {token}"
    url = f"https://api.telegram.org/bot{settings.TOKEN_BOT}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': mensaje})

@csrf_protect
def segundo_factor(request):
    usuario_tmp = request.session.get('usuario_tmp')
    token_valido = request.session.get('token_2fa')
    expira = request.session.get('expira_2fa')

    if not usuario_tmp or not token_valido or not expira or time.time() > expira:
        request.session.flush()
        messages.error(request, "Token inválido o expirado. Intenta iniciar sesión de nuevo.")
        return redirect('login')

    if request.method == 'GET':
        return render(request, 'segundo_factor.html')

    token_ingresado = request.POST.get('token', '').strip()
    if token_ingresado == token_valido:
        request.session.flush()
        request.session['usuario'] = usuario_tmp
        return redirect('dashboard')
    else:
    	return redirect('login')
    messages.error(request, "Token incorrecto.")
    return render(request, 'segundo_factor.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def dashboard(request):
    if not request.session.get('usuario'):
        return redirect('login')
    return render(request, 'dashboard.html', {'section': 'dashboard'})
