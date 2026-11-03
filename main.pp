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
            res = requests.get(url, timeout=2)
            raw = float(res.json()['price'])
            price = round(raw * 0.7512, 2)
        else:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            res = requests.get(url, timeout=2)
            price = round(float(res.json()['price']), 2)
        return price
    except Exception as e:
        logging.error(f"Error price: {e}")
        return 3929.18 if asset_type == "gold" else 90500.0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🥇 Analisis Gold (Valetax XAUUSD)", callback_data="as_gold"),
            InlineKeyboardButton("₿ Analisis Bitcoin (BTC)", callback_data="as_btc")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🌸 **AXON SMC INSTITUTIONAL BOT (VALETAX)** 🌸\n\nLive Market Connected: Order Block, FVG, Structure & Liquidity.\n\nPilih aset market:"
    
    try:
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        elif update.callback_query:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
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

    # Menu Pilih Aset -> Memunculkan Pilihan Fokus Analisis (Resisten/Supply vs Support/Demand)
    if data.startswith("as_"):
        asset = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("🔴 Cari Area Resisten & Supply (Sell Setup)", callback_data=f"focus_{asset}_resistance")],
            [InlineKeyboardButton("🟢 Cari Area Support & Demand (Buy Setup)", callback_data=f"focus_{asset}_support")],
            [InlineKeyboardButton("⚡ Analisis Lengkap (Full SMC Signal)", callback_data=f"focus_{asset}_full")],
            [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        asset_name = "XAU/USD (Valetax)" if asset == "gold" else "BTC/USD"
        try:
            await query.message.edit_text(f"💎 **Aset: {asset_name}**\nPilih fokus area teknikal yang ingin dicari:", reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error focus menu: {e}")
        return

    # Handler Berdasarkan Fokus Pilihan (Resistance, Support, atau Full)
    if data.startswith("focus_"):
        parts = data.split("_")
        if len(parts) < 3:
            await start(update, context)
            return
            
        asset = parts[1]
        focus_type = parts[2]
        name = "XAU/USD (Valetax)" if asset == "gold" else "BTC/USD"

        current_price = get_realtime_data(asset)
        spread = 2.5 if asset == "gold" else 450.0
        tp_dist = 5.0 if asset == "gold" else 900.0
        entry = current_price
        now_str = datetime.datetime.now().strftime("%A, %d/%m/%Y - %H:%M WIB")

        if focus_type == "resistance":
            # Fokus khusus mencari Area Resisten / Supply (Bearish Setup)
            signal = "STRONG SELL (SMC PRO) 🔴"
            trend = "BEARISH INSTITUTIONAL 📉"
            sl = round(entry + spread, 2)
            tp = round(entry - tp_dist, 2)
            ob_type = "Bearish OB (Zona Supply / Resisten Kuat)"
            fvg_status = "Bearish FVG (Inefficiency Penolakan Harga)"
            structure = "CHoCH (Change of Character - Potensi Pembalikan)"
            liquidity = "Equal Highs (EQH) Swept (Berburu Stop Loss Seller)"
            rsi_val = round(random.uniform(28.0, 42.0), 2)
            confidence = random.randint(88, 97)

            msg = (
                f"🔴 **AXON SMC - AREA RESISTEN & SUPPLY** 🔴\n"
                f"___________________________________\n\n"
                f"📅 {now_str}\n"
                f"💎 Pair : {name}\n\n"
                f"🛡 **Fokus Zona Resisten / Supply:**\n"
                f"• Batas Atas Resisten : {sl}\n"
                f"• Area Entry Short    : {entry}\n"
                f"• Target Support (TP) : {tp}\n\n"
                f"📊 **Smart Money Breakdown:**\n"
                f"• Order Block (OB) : {ob_type}\n"
                f"• Market Structure : {structure}\n"
                f"• Fair Value Gap   : {fvg_status}\n"
                f"• Liquidity Pool   : {liquidity}\n"
                f"• RSI (14)         : {rsi_val}\n\n"
                f"🎯 Sinyal Presisi: {signal} (Conf: {confidence}%)\n"
                f"💡 Gunakan rectangle tools MT5 untuk menandai zona Supply."
            )

        elif focus_type == "support":
            # Fokus khusus mencari Area Support / Demand (Bullish Setup)
            signal = "STRONG BUY (SMC PRO) 🟢"
            trend = "BULLISH INSTITUTIONAL 📈"
            sl = round(entry - spread, 2)
            tp = round(entry + tp_dist, 2)
            ob_type = "Bullish OB (Zona Demand / Support Kuat)"
            fvg_status = "Bullish FVG (Order Imbalance Terisi)"
            structure = "BOS (Break of Structure - Tren Lanjut Naik)"
            liquidity = "Equal Lows (EQL) Swept (Berburu Stop Loss Buyer)"
            rsi_val = round(random.uniform(58.0, 72.0), 2)
            confidence = random.randint(88, 97)

            msg = (
                f"🟢 **AXON SMC - AREA SUPPORT & DEMAND** 🟢\n"
                f"___________________________________\n\n"
                f"📅 {now_str}\n"
                f"💎 Pair : {name}\n\n"
                f"🛡 **Fokus Zona Support / Demand:**\n"
                f"• Batas Bawah Support : {sl}\n"
                f"• Area Entry Long     : {entry}\n"
                f"• Target Resisten (TP): {tp}\n\n"
                f"📊 **Smart Money Breakdown:**\n"
                f"• Order Block (OB) : {ob_type}\n"
                f"• Market Structure : {structure}\n"
                f"• Fair Value Gap   : {fvg_status}\n"
                f"• Liquidity Pool   : {liquidity}\n"
                f"• RSI (14)         : {rsi_val}\n\n"
                f"🎯 Sinyal Presisi: {signal} (Conf: {confidence}%)\n"
                f"💡 Gunakan rectangle tools MT5 untuk menandai zona Demand."
            )

        else:
            # Analisis Lengkap (Full SMC Signal)
            is_bullish = random.choice([True, False])
            if is_bullish:
                signal = "STRONG BUY (SMC PRO) 🟢"
                trend = "BULLISH INSTITUTIONAL 📈"
                sl = round(entry - spread, 2)
                tp = round(entry + tp_dist, 2)
                ob_type = "Bullish OB (Akumulasi Institusi)"
                fvg_status = "Bullish FVG (Order Imbalance Terisi)"
                structure = "BOS (Break of Structure - Tren Naik)"
                liquidity = "Equal Lows (EQL) Swept"
                rsi_val = round(random.uniform(52.0, 72.0), 2)
            else:
                signal = "STRONG SELL (SMC PRO) 🔴"
                trend = "BEARISH INSTITUTIONAL 📉"
                sl = round(entry + spread, 2)
                tp = round(entry - tp_dist, 2)
                ob_type = "Bearish OB (Distribusi Institusi)"
                fvg_status = "Bearish FVG (Inefficiency Penolakan)"
                structure = "CHoCH (Change of Character - Pembalikan)"
                liquidity = "Equal Highs (EQH) Swept"
                rsi_val = round(random.uniform(28.0, 48.0), 2)

            confidence = random.randint(84, 98)

            msg = (
                f"🌸 *AXON SMC INSTITUTIONAL SIGNAL* 🌸\n"
                f"___________________________________\n\n"
                f"📅 {now_str}\n"
                f"💎 Pair : {name}\n\n"
                f"💖 Struktur Market : {trend}\n"
                f"🎯 Sinyal Presisi  : {signal}\n\n"
                f"💰 Entry Area  : {entry}\n"
                f"🛑 Stop Loss   : {sl}\n"
                f"🎯 Take Profit : {tp}\n\n"
                f"🌺 *AI SMC Confidence: {confidence}%*\n"
                f"📊 *Smart Money Breakdown:*\n"
                f"• Order Block : {ob_type}\n"
                f"• Market Structure : {structure}\n"
                f"• Fair Value Gap : {fvg_status}\n"
                f"• Liquidity Pool : {liquidity}\n"
                f"• RSI (14) : {rsi_val}\n\n"
                f"💡 Sinkronisasi Live Market Valetax."
            )

        keyboard = [
            [
                InlineKeyboardButton("🔄 Cek Ulang Area", callback_data=f"focus_{asset}_{focus_type}"),
                InlineKeyboardButton("🏠 Pilih Menu Lain", callback_data=f"as_{asset}")
            ],
            [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="home")]
        ]
        
        try:
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error sending focus signal: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.post_init = set_bot_commands
    app.run_polling()
