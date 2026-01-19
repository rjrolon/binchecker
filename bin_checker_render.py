import os
import requests
from threading import Thread
from flask import Flask
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# --- CONFIGURACIÓN DE VARIABLES DE ENTORNO ---
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
RAPIDAPI_KEY = os.environ["RAPIDAPI_KEY"]
RAPIDAPI_HOST = "bin-ip-checker.p.rapidapi.com"

# --- SERVIDOR FLASK (PARA MANTENER VIVO A RENDER) ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "¡El Bot está vivo y corriendo!"

def run():
    # Render asigna un puerto en la variable de entorno PORT. 
    # Si no existe, usamos 8080 por defecto.
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- LÓGICA DEL BOT ---

async def check_bin(update, context: ContextTypes.DEFAULT_TYPE):
    bin_number = update.message.text.strip()
    
    # Validación simple: solo números y al menos 6 dígitos
    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text("Enviame al menos los primeros 6 dígitos (BIN).")
        return

    # Llamada a la API
    url = f"https://{RAPIDAPI_HOST}/?bin={bin_number}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status() # Lanza error si la API falla (404, 500, etc)
        data = r.json()

        if not data.get("success", True): # Algunas APIs devuelven success: false
             await update.message.reply_text("No se encontró información para este BIN.")
             return

        bin_info = data.get("BIN", {})
        issuer = bin_info.get("issuer", {})
        country_obj = bin_info.get("country", {})

        bank = issuer.get("name", "Desconocido")
        country = country_obj.get("name", "Desconocido")
        scheme = bin_info.get("scheme", "Desconocido")
        card_type = bin_info.get("type", "Desconocido")
        level = bin_info.get("level", "Desconocido")

        msg = (
            f"BIN: {bin_number}\n"
            f"Banco: {bank}\n"
            f"País: {country}\n"
            f"Esquema: {scheme}\n"
            f"Tipo: {card_type}\n"
            f"Nivel: {level}"
        )
        await update.message.reply_text(msg)
    
    except Exception as e:
        print(f"Error consultando API: {e}")
        await update.message.reply_text("Hubo un error consultando el BIN. Intenta más tarde.")

def main():
    # 1. Iniciamos el servidor web en un hilo separado
    keep_alive()
    
    # 2. Iniciamos el bot
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_bin))
    print("Bot iniciado...")
    app.run_polling()

if __name__ == "__main__":
    main()
