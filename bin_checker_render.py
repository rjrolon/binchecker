import os
import requests
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
RAPIDAPI_KEY = os.environ["RAPIDAPI_KEY"]
RAPIDAPI_HOST = "bin-ip-checker.p.rapidapi.com"

async def check_bin(update, context: ContextTypes.DEFAULT_TYPE):
    bin_number = update.message.text.strip()
    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text("Enviame al menos los primeros 6 dígitos (BIN).")
        return

    url = f"https://{RAPIDAPI_HOST}/?bin={bin_number}"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }

    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

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

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_bin))
    app.run_polling()

if __name__ == "__main__":
    main()
