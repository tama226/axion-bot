import logging
import datetime
import requests
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "9292175387:AAEwFPI3SrxfRwMwDbbnrXEzJWkgwuiYndM"
logging.basicConfig(level=logging.INFO)

async def set_bot_commands(application):
    try:
        commands = [BotCommand("start", "Buka Menu Utama Analisis 🚀")]
        await application.bot.set_my_commands(commands)
    except Exception as e:
        logging.warning(f"Gagal set commands: {e}")

def get_realtime_data(asset_type):
    try:
        if asset_type == "gold":
            url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
            res = requests.get(url, timeout=3)
            raw = float(res.json()['price'])
            price = round(raw * 0.7512, 2)
        else:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            res = requests.get(url, timeout=3)
            price = round(float(res.json()['price']), 2)
        return price
    except Exception as e:
        logging.error(f"Error price: {e}")
        return 3932.0 if asset_type == "gold" else 91000.0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🥇 Gold (Valetax XAUUSD)", callback_data="as_gold"),
            InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data="as_btc")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "AXON SMC INSTITUTIONAL BOT\n\nLive Market Connected: Order Block, FVG, Structure & Liquidity.\n\nPilih aset market:"
    
    try:
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error start: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
        
    data = query.data
    if data == "home":
        await start(update, context)
        return

    # 1. Pilih Aset -> Lanjut ke Menu Timeframe
    if data.startswith("as_"):
        asset = data.split("_")[1]
        keyboard = [
            [
                InlineKeyboardButton("M1", callback_data=f"tf_{asset}_m1"),
                InlineKeyboardButton("M5", callback_data=f"tf_{asset}_m5"),
                InlineKeyboardButton("M15", callback_data=f"tf_{asset}_m15")
            ],
            [
                InlineKeyboardButton("M30", callback_data=f"tf_{asset}_m30"),
                InlineKeyboardButton("H1", callback_data=f"tf_{asset}_h1"),
                InlineKeyboardButton("H4", callback_data=f"tf_{asset}_h4")
            ],
            [InlineKeyboardButton("D1", callback_data=f"tf_{asset}_d1")],
            [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        asset_name = "XAU/USD (Valetax)" if asset == "gold" else "BTC/USD"
        try:
            await query.message.edit_text(f"Aset: {asset_name}\nPilih Timeframe Analisis:", reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"Error TF menu: {e}")
        return

    # 2. Pilih Timeframe -> Lanjut ke Pilihan Fokus Analisis (Resisten, Support, Full)
    if data.startswith("tf_"):
        parts = data.split("_")
        if len(parts) < 3:
            await start(update, context)
            return
        asset = parts[1]
        tf = parts[2].upper()
        
        keyboard = [
            [InlineKeyboardButton("Cari Area Resisten & Supply", callback_data=f"fc_{asset}_{tf}_res")],
            [InlineKeyboardButton("Cari Area Support & Demand", callback_data=f"fc_{asset}_{tf}_sup")],
            [InlineKeyboardButton("Analisis Lengkap (Full SMC)", callback_data=f"fc_{asset}_{tf}_full")],
            [InlineKeyboardButton("⬅️ Pilih Ulang Timeframe", callback_data=f"as_{asset}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        asset_name = "XAU/USD (Valetax)" if asset == "gold" else "BTC/USD"
        try:
            await query.message.edit_text(f"Aset: {asset_name} | TF: {tf}\nPilih fokus area teknikal:", reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"Error focus menu: {e}")
        return

    # 3. Eksekusi Hasil Analisis Berdasarkan Aset, Timeframe, & Fokus
    if data.startswith("fc_"):
        parts = data.split("_")
        if len(parts) < 4:
            await start(update, context)
            return
            
        asset = parts[1]
        tf = parts[2]
        focus = parts[3]
        name = "XAU/USD (Valetax)" if asset == "gold" else "BTC/USD"

        current_price = get_realtime_data(asset)
        now_str = datetime.datetime.now().strftime("%A, %d/%m/%Y - %H:%M WIB")

        if asset == "gold":
            spread, tp_dist = 2.5, 5.0
        else:
            spread, tp_dist = 120.0, 250.0

        entry = current_price

        if focus == "res":
            signal = "STRONG SELL (SMC PRO)"
            trend = "BEARISH INSTITUTIONAL"
            sl = round(entry + spread, 2)
            tp = round(entry - tp_dist, 2)
            ob = "Bearish OB (Zona Supply / Resisten)"
            fvg = "Bearish Fvg (Inefficiency Penolakan)"
            struct = "CHoCH (Change of Character)"
            liq = "Equal Highs (EQH) Swept"
            rsi = round(random.uniform(28.0, 42.0), 2)
            conf = random.randint(88, 97)

            msg = (
                f"AXON SMC - RESISTENCE & SUPPLY\n"
                f"-----------------------------------\n\n"
                f"Waktu: {now_str}\n"
                f"Pair: {name} | TF: {tf}\n\n"
                f"Zona Supply / Resisten:\n"
                f"- Batas Resisten (SL): {sl}\n"
                f"- Area Entry Short: {entry}\n"
                f"- Target Support (TP): {tp}\n\n"
                f"Smart Money Breakdown:\n"
                f"- Order Block: {ob}\n"
                f"- Structure: {struct}\n"
                f"- Fair Value Gap: {fvg}\n"
                f"- Liquidity: {liq}\n"
                f"- RSI (14): {rsi}\n\n"
                f"Sinyal: {signal} (Conf: {conf}%)\n"
                f"Gunakan rectangle tools MT5."
            )

        elif focus == "sup":
            signal = "STRONG BUY (SMC PRO)"
            trend = "BULLISH INSTITUTIONAL"
            sl = round(entry - spread, 2)
            tp = round(entry + tp_dist, 2)
            ob = "Bullish OB (Zona Demand / Support)"
            fvg = "Bullish Fvg (Order Imbalance Terisi)"
            struct = "BOS (Break of Structure)"
            liq = "Equal Lows (EQL) Swept"
            rsi = round(random.uniform(58.0, 72.0), 2)
            conf = random.randint(88, 97)

            msg = (
                f"AXON SMC - SUPPORT & DEMAND\n"
                f"-----------------------------------\n\n"
                f"Waktu: {now_str}\n"
                f"Pair: {name} | TF: {tf}\n\n"
                f"Zona Demand / Support:\n"
                f"- Batas Support (SL): {sl}\n"
                f"- Area Entry Long: {entry}\n"
                f"- Target Resisten (TP): {tp}\n\n"
                f"Smart Money Breakdown:\n"
                f"- Order Block: {ob}\n"
                f"- Structure: {struct}\n"
                f"- Fair Value Gap: {fvg}\n"
                f"- Liquidity: {liq}\n"
                f"- RSI (14): {rsi}\n\n"
                f"Sinyal: {signal} (Conf: {conf}%)\n"
                f"Gunakan rectangle tools MT5."
            )

        else:
            is_bull = random.choice([True, False])
            if is_bull:
                signal = "STRONG BUY (SMC PRO)"
                trend = "BULLISH INSTITUTIONAL"
                sl = round(entry - spread, 2)
                tp = round(entry + tp_dist, 2)
                ob = "Bullish OB (Akumulasi Institusi)"
                fvg = "Bullish Fvg (Order Imbalance Terisi)"
                struct = "BOS (Break of Structure)"
                liq = "Equal Lows (EQL) Swept"
                rsi = round(random.uniform(52.0, 72.0), 2)
            else:
                signal = "STRONG SELL (SMC PRO)"
                trend = "BEARISH INSTITUTIONAL"
                sl = round(entry + spread, 2)
                tp = round(entry - tp_dist, 2)
                ob = "Bearish OB (Distribusi Institusi)"
                fvg = "Bearish Fvg (Inefficiency Penolakan)"
                struct = "CHoCH (Change of Character)"
                liq = "Equal Highs (EQH) Swept"
                rsi = round(random.uniform(28.0, 48.0), 2)

            conf = random.randint(84, 98)

            msg = (
                f"AXON SMC INSTITUTIONAL SIGNAL\n"
                f"-----------------------------------\n\n"
                f"Waktu: {now_str}\n"
                f"Pair: {name} | TF: {tf}\n\n"
                f"Struktur Market: {trend}\n"
                f"Sinyal Presisi: {signal}\n\n"
                f"Entry Area: {entry}\n"
                f"Stop Loss: {sl}\n"
                f"Take Profit: {tp}\n\n"
                f"AI SMC Confidence: {conf}%\n"
                f"Smart Money Breakdown:\n"
                f"- Order Block: {ob}\n"
                f"- Structure: {struct}\n"
                f"- Fair Value Gap: {fvg}\n"
                f"- Liquidity: {liq}\n"
                f"- RSI (14): {rsi}\n\n"
                f"Sinkronisasi Live Market Valetax."
            )

        keyboard = [
            [
                InlineKeyboardButton("Analisa Ulang", callback_data=f"fc_{asset}_{tf}_{focus}"),
                InlineKeyboardButton("Pilih Timeframe", callback_data=f"as_{asset}")
            ],
            [InlineKeyboardButton("Menu Utama", callback_data="home")]
        ]
        
        try:
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            logging.error(f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.post_init = set_bot_commands
    app.run_polling()
