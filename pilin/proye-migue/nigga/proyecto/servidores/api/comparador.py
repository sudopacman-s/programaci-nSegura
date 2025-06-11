from plataforma.API import hasheador

def comparar_hashes(hash_existente: str, contraseña_comparar: str) -> bool:
    """
    Compara un hash con el hash de una contraseña que acaba de recibir.

    hash_existente: str, hash de la contraseña almacenada
    contraseña_comparar: str, nueva contraseña a verificar
    returns: bool, True si los hashes coinciden, False en caso contrario
    """
    hash_comparar=hasheador.hashing(contraseña_comparar)

    return hash_existente == hash_comparar
