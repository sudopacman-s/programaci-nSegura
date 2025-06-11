import hashlib
import base64

def hashing(nueva_pass: str) -> bool:
    """
    Determina si la nueva contraseña coincide con el hash guardado.

    nueva_pass: str, nueva contraseña a verificar
    hash_guardado: str, hash de la contraseña almacenada
    returns: bool, True si la nueva contraseña coincide con el hash guardado
    """
    formato = '$6$wLn3hfSJdxalxrpH$'
    _, algoritmo, salt, _ = formato.split('$')
    hash_obj = hashlib.sha512()
    hash_obj.update(nueva_pass.encode('utf-8') + base64.b64decode(salt))
    nuevo_hash = '$%s$%s$%s' % (algoritmo, salt, hash_obj.hexdigest())
    print(nuevo_hash)
    return nuevo_hash
