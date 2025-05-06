import subprocess
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario, Servidor
from django.views.decorators.csrf import csrf_protect
import hashlib, paramiko, os
from django.conf import settings
from datetime import datetime  
from django.http import HttpResponse

@csrf_protect
def login_usuario(request):
    if request.method == 'POST':
        usuario = request.POST.get('nombre_usuario')
        contrasena = request.POST.get('contrasena')
        hash_contrasena = hashlib.sha256(contrasena.encode()).hexdigest()

        try:
            usuario_obj = Usuario.objects.get(nombre_usuario=usuario)
            if usuario_obj.contrasena_sha256 == hash_contrasena:
                request.session['usuario'] = usuario
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
    return render(request, 'login.html')

def logout_usuario(request):
    request.session.flush()
    return redirect('login')

def registrar_servidor(request):
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

def dashboard(request):
    if 'usuario' not in request.session:
        return redirect('login')

    # Verificar si se debe crear un archivo en un servidor
    if request.method == 'POST' and 'crear_archivo' in request.POST:
        servidor_id = request.POST.get('servidor_id')
        return crear_archivo(request, servidor_id)

    servidores = Servidor.objects.all()
    estado_servidores = []

    for s in servidores:
        host = s.obtener_host()
        respuesta = subprocess.run(["ping", "-c", "3", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        salida = respuesta.stdout.decode()

        if "100% packet loss" in salida or "Destination Host Unreachable" in salida:
            estado = 'rojo'
        elif "0% packet loss" in salida:
            estado = 'verde'
        else:
            estado = 'amarillo'

        estado_servidores.append((s.id, host, estado))

    return render(request, 'dashboard.html', {'estado_servidores': estado_servidores})
    
def crear_archivo(request, servidor_id):
    if 'usuario' not in request.session:
        return redirect('login')

    try:
        servidor = Servidor.objects.get(id=servidor_id)
        host = servidor.obtener_host()
        usuario = servidor.obtener_usuario()
        contrasena = servidor.obtener_contrasena()

        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(host, username=usuario, password=contrasena)

        comando = "echo 'Archivo creado' > perro.txt"
        cliente.exec_command(comando)
        cliente.close()
        messages.success(request, f'Archivo creado en {host}')
    except Exception as e:
        messages.error(request, f'Error al crear archivo: {e}')

    return redirect('dashboard')

