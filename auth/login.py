import threading, requests, time, webbrowser, json
from flask import Flask, request

APP_ID = "123456789"  # reemplazar con tu app id
APP_SECRET = "abdcdef1234567890"  # reemplazar con tu client secret
REDIRECT_URI = "https://abc123.xyz/callback" # reemplazar con tu redirect uri


def save_tokens(response_json):

    tokens = {
        "access_token": response_json["access_token"],
        "refresh_token": response_json["refresh_token"],
        "expires_at": time.time() + response_json["expires_in"]
    }

    with open("auth/tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)

    return tokens


def interactive_login():
    app = Flask(__name__)

    result = {}

    @app.route('/callback')
    def callback():
        code = request.args.get('code')

        response = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            headers={
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "client_id": APP_ID,
                "client_secret": APP_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI
            }
        )

        result["tokens"] = save_tokens(response.json())

        shutdown = request.environ.get("werkzeug.server.shutdown")

        if shutdown:
            shutdown()

        return "Login correcto."
    
    auth_url = (
        "https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code"
        f"&client_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )

    threading.Timer(1, lambda: webbrowser.open(auth_url)).start()

    app.run(port=8080)

    return result.get("tokens")

def refresh_tokens(tokens):

    response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        headers={
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "refresh_token",
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "refresh_token": tokens["refresh_token"]
        }
    )

    if response.status_code != 200:
        return None

    return save_tokens(response.json())


def get_tokens():

    try:

        with open("auth/tokens.json", "r") as f:
            tokens = json.load(f)

    except Exception:

        print("No existe tokens.json")
        print("Iniciando login interactivo...")

        return interactive_login()

    print("Refrescando token...")

    refreshed = refresh_tokens(tokens)

    if refreshed:

        print("Token refrescado.")

        return refreshed

    print("Refresh fallo.")
    print("Iniciando login interactivo...")

    return interactive_login()