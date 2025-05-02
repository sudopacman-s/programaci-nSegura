from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Servidor
import paramiko
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

def registrar_servidor(request):
    if request.method == 'POST':
        host = request.POST.get('host')
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')

        cliente_ssh = paramiko.SSHClient()
        cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            cliente_ssh.connect(hostname=host, username=usuario, password=contrasena)

            fecha_hora = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            mensaje_log = f"Se ha registrado a la aplicación el día {fecha_hora}\n"
            comando_log = f"echo '{mensaje_log}' | sudo tee -a /var/log/administrador.log"
            cliente_ssh.exec_command(comando_log)

            nuevo_servidor = Servidor()
            nuevo_servidor.guardar_datos(host, usuario, contrasena)
            nuevo_servidor.save()

            cliente_ssh.close()

            # Guardar el ID del servidor en sesión
            request.session['servidor_id'] = nuevo_servidor.id

            return redirect('dashboard')

        except Exception as e:
            print(f"[ERROR] No se pudo registrar: {e}")
            return render(request, 'registrar.html', {'error': '❌ No se pudo registrar. Verifica la conexión y credenciales.'})

    return render(request, 'registrar.html')


@csrf_exempt
def dashboard(request):
    servidor_id = request.session.get('servidor_id')

    if not servidor_id:
        return HttpResponse("No hay un servidor registrado en esta sesión.", status=400)

    try:
        servidor = Servidor.objects.get(id=servidor_id)
        host = servidor.obtener_host()
        usuario = servidor.obtener_usuario()
        contrasena = servidor.obtener_contrasena()

        mensaje = ""

        if request.method == 'POST':
            mensaje = crear_archivo_txt(host, usuario, contrasena)

        return render(request, 'dashboard.html', {
            'host': host,
            'usuario': usuario,
            'mensaje': mensaje
        })

    except Servidor.DoesNotExist:
        return HttpResponse("Servidor no encontrado", status=404)


def crear_archivo_txt(host, usuario, contrasena):
    try:
        cliente_ssh = paramiko.SSHClient()
        cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente_ssh.connect(hostname=host, username=usuario, password=contrasena)

        comando = "echo 'Archivo perro creado con éxito' > perro.txt"
        cliente_ssh.exec_command(comando)
        cliente_ssh.close()

        return "✅ Archivo perro.txt creado en el servidor remoto."

    except Exception as e:
        print(f"[ERROR] Al crear archivo: {e}")
        return "❌ No se pudo crear el archivo perro.txt."

