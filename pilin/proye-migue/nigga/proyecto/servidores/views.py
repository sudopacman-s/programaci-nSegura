import subprocess
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario, Servidor, ContadorIntentos
from django.views.decorators.csrf import csrf_protect
import hashlib, paramiko, os
from django.conf import settings
from datetime import datetime
from datetime import timezone
from django.http import HttpResponse
from .api.telegram import enviar_token_telegram
from .api.validarcaptcha import validar_recaptcha
from .api.hasheador import hashing
#from .api.intentos import tienes_intentos_login
import random
import string
import requests
import time


def enviar_token_telegram(chat_id, token):
    mensaje = f"Tu token de acceso es: {token}"
    url = f"https://api.telegram.org/bot{settings.TOKEN_BOT}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': mensaje})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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
        return render(request, 'login.html', {
            'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY
        })

    usuario = request.POST.get('nombre_usuario', '').strip()
    contrasena = request.POST.get('contrasena', '').strip()
    respuesta = request.POST.get('captcha', '').strip()

    errores = []

    if not tienes_intentos_login(request):
        errores.append(f'Debes esperar {settings.SEGUNDOS_INTENTO} segundos antes de volver a intentar')
        return render(request, 'login.html', {
            'errores': errores,
            'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY
        })

    if not usuario or not contrasena:
        errores.append('Usuario y contraseña son obligatorios.')

    if not validar_recaptcha(request):
        errores.append('Por favor, completa el reCAPTCHA.')

    if errores:
        return render(request, 'login.html', {
            'errores': errores,
            'usuario': usuario,
            'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY
        })

    hash_contrasena = hashing(contrasena)
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

    return render(request, 'login.html', {
        'errores': errores,
        'usuario': usuario,
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY
    })

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
    	request.session.flush()
    	return redirect('login')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def dashboard(request):
    if not request.session.get('usuario'):
        return redirect('login')

    if request.method == 'POST':
        servidor_id = request.POST.get('servidor_id')
        request.session['servidor_id'] = servidor_id
        return redirect('detalle_servidor')

    servidores = Servidor.objects.all()
    servidores_info = []

    for servidor in servidores:
        host = servidor.obtener_host()
        # Comprobación de disponibilidad con ping
        try:
            resultado_ping = subprocess.run(
                ['ping', '-c', '1', host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            activo = resultado_ping.returncode == 0
        except Exception:
            activo = False

        servidores_info.append({
            'id': servidor.id,
            'host': host,
            'activo': activo
        })

    return render(request, 'dashboard.html', {'servidores': servidores_info})
    
def detalle_servidor(request):
    if not request.session.get('usuario'):
        return redirect('login')

    servidor_id = request.session.get('servidor_id')
    if not servidor_id:
        return redirect('dashboard')

    try:
        servidor = Servidor.objects.get(pk=servidor_id)
        host = servidor.obtener_host()
        usuario = servidor.obtener_usuario()
        contrasena = servidor.obtener_contrasena()

        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(hostname=host, username=usuario, password=contrasena, timeout=10)

        stdin, stdout, stderr = cliente.exec_command('uname -a && uptime && whoami')
        salida = stdout.read().decode()
        cliente.close()

        return render(request, 'detalle_servidor.html', {
            'host': host,
            'info': salida
        })

    except Servidor.DoesNotExist:
        return HttpResponse("Servidor no encontrado.")
    except Exception as e:
        return HttpResponse(f"Error al conectar: {str(e)}")


def registrar_servidor(request):
    if not request.session.get('usuario'):
        return redirect('login')
    if request.method == 'POST':
        host = request.POST.get('host')
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')

        try:
            # 1. Verificar conexión SSH primero
            cliente = paramiko.SSHClient()
            cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cliente.connect(hostname=host, username=usuario, password=contrasena, timeout=10)

            # 2. Registrar en logs del servidor
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mensaje = f"Registro en aplicación: {fecha_actual}\n"
            comando = f'echo "{mensaje}" | sudo tee -a /var/log/administrador.log'
            cliente.exec_command(comando)
            cliente.close()

            # 3. Guardar en base de datos (con cifrado)
            servidor = Servidor()
            servidor.guardar_datos(host, usuario, contrasena)  # ¡Usa el nuevo método!
            servidor.save()

            return redirect('dashboard')

        except paramiko.AuthenticationException:
            return HttpResponse("Error: Credenciales SSH inválidas")
        except paramiko.SSHException as e:
            return HttpResponse(f"Error de conexión SSH: {str(e)}")
        except Exception as error:
            return HttpResponse(f"Error inesperado: {str(error)}")

    return render(request, 'registrar_servidor.html')
