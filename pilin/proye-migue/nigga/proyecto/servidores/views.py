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
import re

import random
import string
import requests
import time

# Permitir solo nombres válidos de servicios (evita inyección)
SERVICIO_REGEX = re.compile(r'^[a-zA-Z0-9_.@-]+\.service$')

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
    """
    Funcion login para autenticar usuario mediante credenciales,
    captcha y OTP, implementando límite de intentos.
    """
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
    """
    Funcion para enviar  y verificar token OTP enviado por telegram.
    """
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
    """
    Funcion para eliminar la sesión y cerrarla, redirige a login.
    """
    request.session.flush()
    return redirect('login')

def ejecutar_comando_ssh(host, usuario, contrasena, comando, sudo_pass=None):
    """
    Funcion para ejecutar comandos en servidor remoto.
    """
    try:
        cli = paramiko.SSHClient()
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cli.connect(hostname=host, username=usuario, password=contrasena, timeout=5)
        if sudo_pass:
            comando = f"echo '{sudo_pass}' | sudo -S {comando}"
        stdin, stdout, stderr = cli.exec_command(comando, timeout=10)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        cli.close()
        return out, err
    except Exception as e:
        return "", f"Error SSH: {e}"

def dashboard(request):
    """
    Funcion para probar conexión con servidores remotos y mostrarlos en la pagina principal.
    """
    if not request.session.get('usuario'):
        return redirect('login')

    if request.method == 'POST':
        request.session['servidor_id'] = request.POST['servidor_id']
        request.session.pop('servicio_seleccionado', None)
        return redirect('detalle_servidor')

    info = []
    for s in Servidor.objects.all():
        host = s.obtener_host()
        activo = subprocess.run(['ping','-c','1',host],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL).returncode == 0
        info.append({'id': s.id, 'host': host, 'activo': activo})
    return render(request, 'dashboard.html', {'servidores': info})

def detalle_servidor(request):
    """
    Muestre detalles del servidor, así como los servicios y campo para levantar servicio.
    Lista todos los servicios filtrados activos.
    """
    if not request.session.get('usuario'):
        return redirect('login')
    sid = request.session.get('servidor_id')
    if not sid:
        return redirect('dashboard')

    try:
        s = Servidor.objects.get(pk=sid)
    except Servidor.DoesNotExist:
        messages.error(request, "Servidor no encontrado.")
        return redirect('dashboard')

    servidor = {
        'host': s.obtener_host(),
        'usuario': s.obtener_usuario(),
        'contrasena': s.obtener_contrasena()
    }

    # Levantar servicio (POST desde este mismo template)
    if request.method == 'POST' and 'nombre_servicio' in request.POST:
        nombre = request.POST['nombre_servicio'].strip()
        sudo_pwd = request.POST.get('sudo_password','').strip()
        if not SERVICIO_REGEX.match(nombre):
            messages.error(request, "Servicio inválido.")
        elif not sudo_pwd:
            messages.error(request, "Contraseña sudo requerida.")
        else:
            _, err = ejecutar_comando_ssh(**servidor,
                comando=f"systemctl start {nombre}", sudo_pass=sudo_pwd)
            if err:
                messages.error(request, f"No arrancó {nombre}: {err}")
            else:
                messages.success(request, f"{nombre} arrancado.")
        return redirect('detalle_servidor')

    # Listar servicios activos
    out, err = ejecutar_comando_ssh(**servidor,
        comando="systemctl list-units --type=service --state=active --no-pager --no-legend | awk '{print $1}'")
    servicios = out.splitlines() if out else []
    if err:
        messages.error(request, "No pude listar servicios.")

    return render(request, 'detalle_servidor.html', {
        'servicios': servicios
    })

def detalle_servicio(request):
    """
    Funcion que muestra detalles de cada servicio, así como posibilidad de detenerlo, reiniciarlo o encenderlo.
    """
    if not request.session.get('usuario'):
        return redirect('login')
    sid = request.session.get('servidor_id')
    if not sid:
        return redirect('dashboard')

    # Si vienen aquí seleccionando un servicio:
    if request.method == 'POST' and 'servicio' in request.POST:
        srv = request.POST['servicio'].strip()
        if SERVICIO_REGEX.match(srv):
            request.session['servicio_seleccionado'] = srv
        else:
            messages.error(request, "Servicio inválido.")
        return redirect('detalle_servicio')

    # Ahora, control de start/stop/restart:
    srv = request.session.get('servicio_seleccionado')
    if not srv:
        return redirect('detalle_servidor')

    try:
        s = Servidor.objects.get(pk=sid)
    except Servidor.DoesNotExist:
        return redirect('dashboard')

    servidor = {
        'host': s.obtener_host(),
        'usuario': s.obtener_usuario(),
        'contrasena': s.obtener_contrasena()
    }

    # Acción sobre el servicio
    if request.method == 'POST' and 'accion' in request.POST:
        accion = request.POST['accion']
        sudo_pwd = request.POST.get('sudo_password','').strip()
        if accion not in ['start','stop','restart']:
            messages.error(request, "Acción no permitida.")
        elif not sudo_pwd:
            messages.error(request, "Contraseña sudo requerida.")
        else:
            _, err = ejecutar_comando_ssh(**servidor,
                comando=f"systemctl {accion} {srv}", sudo_pass=sudo_pwd)
            if err:
                messages.error(request, f"No pudo {accion} {srv}: {err}")
            else:
                messages.success(request, f"{srv}: {accion} ejecutado.")
        return redirect('detalle_servicio')

    # GET: mostrar estado
    info, err = ejecutar_comando_ssh(**servidor,
        comando=f"systemctl status {srv} --no-pager")
    if err:
        info = f"Error al obtener estado: {err}"

    return render(request, 'detalle_servicio.html', {
        'nombre_servicio': srv,
        'info_servicio': info
    })

def registrar_servidor(request):
    """
    Funcion para registrar un nuevo servidor mediante un formulario.

    IP
    Usuario: str
    Contraseña: str
    """
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
