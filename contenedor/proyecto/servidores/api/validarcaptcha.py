import requests
from django.conf import settings


def validar_recaptcha(request):
    """
    Verifica si el reCAPTCHA es válido.
    """
    recaptcha_response = request.POST.get('g-recaptcha-response')
    if not recaptcha_response:
        return False

    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': recaptcha_response
    }
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data=data
    )
    result = response.json()
    return result.get('success', False)

