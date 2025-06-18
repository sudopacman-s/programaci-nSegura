import requests
from django.conf import settings

def enviar_token_telegram(chat_id, token):
    mensaje = f"Tu token de acceso es: {token}"
    url = f"https://api.telegram.org/bot{settings.TOKEN_BOT}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': mensaje})
