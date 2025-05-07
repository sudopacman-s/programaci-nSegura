import random

def generar_captcha(request):
    """
    Genera dos números aleatorios para un captcha de suma simple,
    los guarda en la sesión y los retorna.
    """
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    request.session['captcha_a'] = a
    request.session['captcha_b'] = b
    return a, b

def validar_captcha(request, respuesta_usuario):
    """
    Valida que la respuesta del usuario sea igual a la suma almacenada en sesión.
    Elimina los valores de la sesión al finalizar.

    Parámetros:
    - request: HttpRequest
    - respuesta_usuario: str

    Retorna:
    - bool: True si es correcto, False si no lo es.
    """
    try:
        a = int(request.session.pop('captcha_a'))
        b = int(request.session.pop('captcha_b'))
        return int(respuesta_usuario) == a + b
    except (KeyError, ValueError, TypeError):
        return False

