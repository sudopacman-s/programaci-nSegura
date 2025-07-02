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
from django.http import JsonResponse
#from .api.intentos import tienes_intentos_login
import re
import logging
import random
import string
import requests
import time
import ipaddress

#logging.basicConfig(level=logging.INFO,
 #                   filename='app.log',
  #                  filemode='a',
   #                 format='%(asctime)s - %(levelname)s - %(message)s',
    #                datefmt='%d-%b-%y %H:%M:%S')


logger = logging.getLogger("servidores_app")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('app.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Silenciar paramiko
logging.getLogger("paramiko").setLevel(logging.WARNING)

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
                logger.info(f'Usuario {usuario} loggeado')
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
    try:
        cli = paramiko.SSHClient()
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cli.connect(hostname=host, username=usuario, password=contrasena, timeout=5)

        # Si se requiere contraseña sudo (ya no se usará, pero lo dejamos por compatibilidad)
        if sudo_pass:
            comando = f"echo '{sudo_pass}' | sudo -S {comando}"

        stdin, stdout, stderr = cli.exec_command(comando, timeout=10)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        exit_status = stdout.channel.recv_exit_status()
        cli.close()
        return out, err, exit_status
    except Exception as e:
        return "", f"Error SSH: {e}", -1



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
        info.append({'id': s.id, 'host': host, 'activo': activo, 'nombre': s.nombre})
    return render(request, 'dashboard.html', {'servidores': info})

def detalle_servidor(request):
    """
    Muestra detalles del servidor, así como los servicios y campo para levantar servicios.
    Ya no solicita contraseña sudo gracias a configuración NOPASSWD.
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

    servidor_ssh = {
        'host': s.obtener_host(),
        'usuario': s.obtener_usuario(),
        'contrasena': s.obtener_contrasena()
    }
    nombre = s.nombre  # asignamos aquí para usar en render

    # Levantar servicio (POST desde este mismo template)
    if request.method == 'POST' and 'nombre_servicio' in request.POST:
        nombre_servicio = request.POST['nombre_servicio'].strip()

        if not SERVICIO_REGEX.match(nombre_servicio):
            messages.error(request, "Nombre de servicio inválido.")
        else:
            comando = f"sudo systemctl start {nombre_servicio}"
            _, err, exit_code = ejecutar_comando_ssh(**servidor_ssh, comando=comando)
            logger.info(f'Servicio {nombre_servicio} levantado en host: {servidor_ssh["host"]}')
            if exit_code != 0:
                messages.error(request, f"No se pudo iniciar {nombre_servicio}: {err}")
            else:
                messages.success(request, f"{nombre_servicio} iniciado correctamente.")
        return redirect('detalle_servidor')

    # Listar servicios activos
    comando_listar = "systemctl list-units --type=service --state=active --no-pager --no-legend | awk '{print $1}'"
    out, err, _ = ejecutar_comando_ssh(**servidor_ssh, comando=comando_listar)
    servicios = out.splitlines() if out else []
    if err:
        messages.error(request, "No se pudieron listar los servicios activos.")

    return render(request, 'detalle_servidor.html', {
        'servicios': servicios,
        'nombre': nombre
    })


def detalle_servicio(request):
    """
    Muestra detalles de un servicio y permite detenerlo, reiniciarlo o encenderlo sin contraseña sudo.
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

    # Obtener servicio seleccionado
    srv = request.GET.get('servicio') or request.session.get('servicio_seleccionado')
    if srv:
        request.session['servicio_seleccionado'] = srv

    try:
        s = Servidor.objects.get(pk=sid)
    except Servidor.DoesNotExist:
        return redirect('dashboard')

    servidor_ssh = {
        'host': s.obtener_host(),
        'usuario': s.obtener_usuario(),
        'contrasena': s.obtener_contrasena()
    }
    nombre = s.nombre  # Para pasar al template

    # Acción sobre el servicio
    if request.method == 'POST' and 'accion' in request.POST:
        accion = request.POST['accion']
        if accion not in ['start', 'stop', 'restart']:
            messages.error(request, "Acción no permitida.")
        else:
            comando = f"sudo systemctl {accion} {srv}"
            _, err, exit_code = ejecutar_comando_ssh(**servidor_ssh, comando=comando)
            logger.info(f'Servicio {srv} {accion} en host: {servidor_ssh["host"]}')
            if exit_code != 0:
                messages.error(request, f"No se pudo ejecutar {accion}: {err}")
            else:
                messages.success(request, f"{srv}: acción {accion} ejecutada correctamente.")
        return redirect('detalle_servicio')

    # GET: mostrar estado del servicio
    comando_status = f"sudo systemctl status {srv} --no-pager"
    info, err, _ = ejecutar_comando_ssh(**servidor_ssh, comando=comando_status)
    if err:
        info = f"Error al obtener estado: {err}"

    return render(request, 'detalle_servicio.html', {
        'nombre_servicio': srv,
        'info_servicio': info,
        'nombre': nombre
    })



import ipaddress  # Asegúrate de tener este import

def registrar_servidor(request):
    if not request.session.get('usuario'):
        return redirect('login')

    if request.method == 'POST':
        host = request.POST.get('host', '').strip()
        usuario = request.POST.get('usuario', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()
        nombre = request.POST.get('nombre', '').strip()

        if not host or not usuario or not contrasena or not nombre:
            error = "Todos los campos son obligatorios."
            return render(request, 'registrar_servidor.html', {'error': error})

        # Validar IP
        try:
            ipaddress.ip_address(host)
        except ValueError:
            error = "Dirección IP no válida."
            return render(request, 'registrar_servidor.html', {'error': error})

        try:
            # Verificar conexión SSH
            cliente = paramiko.SSHClient()
            cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cliente.connect(hostname=host, username=usuario, password=contrasena, timeout=10)

            # Registrar en logs remotos
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mensaje = f"Registro en aplicación: {fecha_actual}\n"
            comando = f'echo "{mensaje}" | sudo tee -a /var/log/administrador.log'
            cliente.exec_command(comando)
            cliente.close()

            # Guardar en base de datos
            servidor = Servidor()
            servidor.nombre = nombre
            servidor.guardar_datos(host, usuario, contrasena)
            servidor.save()

            logger.info(f'Servidor {host} registrado con nombre: {nombre}')
            return redirect('dashboard')

        except paramiko.AuthenticationException:
            return HttpResponse("Error: Credenciales SSH inválidas")
        except paramiko.SSHException as e:
            return HttpResponse(f"Error de conexión SSH: {str(e)}")
        except Exception as error:
            return HttpResponse(f"Error inesperado: {str(error)}")

    return render(request, 'registrar_servidor.html')



def servicios_activados_json(request):
    """
    Devuelve la lista de servicios activos del servidor actual como JSON.
    """
    if not request.session.get('usuario'):
        return JsonResponse({'error': 'No autorizado'}, status=403)
    sid = request.session.get('servidor_id')
    if not sid:
        return JsonResponse({'error': 'Servidor no definido'}, status=400)

    try:
        s = Servidor.objects.get(pk=sid)
    except Servidor.DoesNotExist:
        return JsonResponse({'error': 'Servidor no encontrado'}, status=404)

    servidor = {
        'host': s.obtener_host(),
        'usuario': s.obtener_usuario(),
        'contrasena': s.obtener_contrasena()
    }

    out, err, _ = ejecutar_comando_ssh(**servidor,
        comando="systemctl list-units --type=service --state=active --no-pager --no-legend | awk '{print $1}'")

    if err:
        return JsonResponse({'error': err}, status=500)

    servicios = out.splitlines() if out else []
    return JsonResponse({'servicios': servicios})
