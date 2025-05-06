from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import hashlib

def generar_fernet():
    clave = settings.SECRET_KEY.encode()
    clave_hash = hashlib.sha256(clave).digest()
    clave_base64 = base64.urlsafe_b64encode(clave_hash)
    return Fernet(clave_base64)

class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=150, unique=True)
    contrasena_sha256 = models.CharField(max_length=255)

class Servidor(models.Model):
    id = models.CharField(primary_key=True, max_length=255)  # host_usuario
    host_cifrado = models.BinaryField()
    usuario_cifrado = models.BinaryField()
    contrasena_cifrada = models.BinaryField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def guardar_datos(self, host, usuario, contrasena):
        fernet = generar_fernet()
        self.id = host.replace('.', '-') + "_" + usuario
        self.host_cifrado = fernet.encrypt(host.encode())
        self.usuario_cifrado = fernet.encrypt(usuario.encode())
        self.contrasena_cifrada = fernet.encrypt(contrasena.encode())

    def obtener_host(self):
        return generar_fernet().decrypt(self.host_cifrado).decode()

    def obtener_usuario(self):
        return generar_fernet().decrypt(self.usuario_cifrado).decode()

    def obtener_contrasena(self):
        return generar_fernet().decrypt(self.contrasena_cifrada).decode()
