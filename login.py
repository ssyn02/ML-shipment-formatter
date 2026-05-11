import os, threading, requests, time, webbrowser, json
from flask import Flask, request

def main():
    APP_ID = "123456789"  # reemplazar con tu app id
    APP_SECRET = "abdcdef1234567890"  # reemplazar con tu client secret
    REDIRECT_URI = "https://abc123.xyz/callback" # reemplazar con tu redirect uri

    app = Flask(__name__)

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

        response_json = response.json()

        tokens = {
            "access_token": response_json["access_token"],
            "refresh_token": response_json["refresh_token"],
            "expires_at": time.time() + response_json["expires_in"]
        }

        with open("tokens.json", "w") as f:
            json.dump(tokens, f, indent=4)

        threading.Timer(1, lambda: os._exit(0)).start()

        return "Login correcto."

    url = f"https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id={APP_ID}&redirect_uri={REDIRECT_URI}"

    webbrowser.open(url)

    app.run(port=8080)

if __name__ == "__main__":
    main()