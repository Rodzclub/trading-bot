#!/usr/bin/env python3
"""
Setup OAuth 2.0 para TD Ameritrade/Thinkorswim
Ejecutar una sola vez: python setup_oauth.py
Genera token.json que se usa automáticamente en thinkorswim_broker.py
"""

import os
import json
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("TD_CONSUMER_KEY")
if not CONSUMER_KEY:
    print("❌ ERROR: TD_CONSUMER_KEY no encontrado en .env")
    print("Pasos:")
    print("1. Ve a: https://developer.tdameritrade.com/")
    print("2. Crea una app y obtén tu Consumer Key")
    print("3. Agrega a .env: TD_CONSUMER_KEY=PK_...")
    exit(1)

REDIRECT_URI = "http://localhost:8000"
TOKEN_FILE = "token.json"
AUTH_URL = "https://auth.tdameritrade.com/auth"
TOKEN_URL = "https://api.tdameritrade.com/v1/oauth2/token"

auth_code = None
auth_received = False


class OAuthHandler(BaseHTTPRequestHandler):
    """Handler para capturar el código de autorización"""

    def do_GET(self):
        global auth_code, auth_received

        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params:
            auth_code = params["code"][0]
            auth_received = True

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            response = """
            <html>
            <head><title>OAuth Exitoso</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>✅ ¡Autorización Exitosa!</h1>
                <p>Tu aplicación está autorizada para acceder a TD Ameritrade.</p>
                <p>Puedes cerrar esta ventana y volver a la terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: No authorization code received")

    def log_message(self, format, *args):
        pass  # Silenciar logs


def setup_oauth():
    """Setup OAuth y obtener token de acceso"""

    print("\n" + "="*60)
    print("🔐 CONFIGURACIÓN OAUTH - TD AMERITRADE")
    print("="*60)

    # Paso 1: Abrir navegador para autorización
    auth_params = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "client_id": CONSUMER_KEY + "@AMER.OAUTHAP",
        "scope": "PlaceTrades AccountAccess MoveMoney"
    }

    auth_request_url = f"{AUTH_URL}?" + "&".join(
        [f"{k}={v}" for k, v in auth_params.items()]
    )

    print("\n1️⃣  Abriendo navegador para autorización...")
    print(f"   URL: {auth_request_url[:50]}...")

    webbrowser.open(auth_request_url)

    # Paso 2: Escuchar callback
    print("\n2️⃣  Esperando respuesta del navegador...")
    print("   Servidor OAuth escuchando en http://localhost:8000")
    print("   → Si ves una página blanca, haz clic en 'Allow'")

    server = HTTPServer(("localhost", 8000), OAuthHandler)

    while not auth_received:
        server.handle_request()

    server.server_close()

    if not auth_code:
        print("❌ No se recibió código de autorización")
        return False

    print(f"✅ Código de autorización recibido")

    # Paso 3: Intercambiar código por token
    print("\n3️⃣  Intercambiando código por token de acceso...")

    token_params = {
        "grant_type": "authorization_code",
        "access_type": "offline",
        "code": auth_code,
        "client_id": CONSUMER_KEY + "@AMER.OAUTHAP",
        "redirect_uri": REDIRECT_URI
    }

    try:
        response = requests.post(TOKEN_URL, data=token_params)
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener token: {e}")
        return False

    # Paso 4: Guardar token
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"✅ Token guardado en: {TOKEN_FILE}")

    # Resumen
    print("\n" + "="*60)
    print("✨ OAUTH CONFIGURADO EXITOSAMENTE")
    print("="*60)
    print(f"✓ Access Token válido por: {token_data.get('expires_in', 1800)} segundos")
    print(f"✓ Token guardado en: {TOKEN_FILE}")
    print(f"✓ Archivo .gitignore: {TOKEN_FILE} ← NO COMITEAR")
    print("\nPróximos pasos:")
    print("1. python thinkorswim_broker.py  → Verifica conexión")
    print("2. python scanner_premarket.py   → Escanea oportunidades")
    print("3. python main.py                → Ejecuta bot")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    success = setup_oauth()
    exit(0 if success else 1)
