#!/usr/bin/env python3
import os
import base64
import hashlib
import secrets
import sys  # Necesario para leer argumentos

def salteado(contraseña):
    # 1. Generar una sal segura (16 bytes)
    sal = secrets.token_bytes(16)
    print("Sal (cruda):", sal)
    
    # 2. Codificar la sal en Base64
    sal_b64 = base64.b64encode(sal).decode('utf-8')
    print("Sal (Base64):", sal_b64)
    
    # 3. Hashear con PBKDF2-HMAC-SHA512 (100,000 iteraciones)
    hasheado = hashlib.pbkdf2_hmac(
        'sha512',
        contraseña.encode('utf-8'),
        sal,
        100000
    )
    hasheado_b64 = base64.b64encode(hasheado).decode('utf-8')
    print("Contraseña hasheada:", hasheado_b64)
    
    return f"$6${sal_b64}${hasheado_b64}"

if __name__ == "__main__":
    # Verificar que se proporcionó un argumento
    if len(sys.argv) < 2:
        print("Uso: python3 negros.py [contraseña]")
        print("Ejemplo: python3 negros.py 'miClaveSecreta'")
        sys.exit(1)
    
    contraseña = sys.argv[1]
    hash_almacenado = salteado(contraseña)
    print("\nHash para almacenar:", hash_almacenado)
