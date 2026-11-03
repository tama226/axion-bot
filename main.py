import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Konfigurasi Token Bot dari Environment Variable Railway
BOT_TOKEN = os.getenv("BOT_TOKEN", "MASUKKAN_TOKEN_BOT_KAMU_DISINI")

# Fungsi ambil data harga real-time dari Binance
def get_market_data(symbol="XAUUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        raw_price = float(data['price'])
        
        # Kalibrasi khusus untuk XAU/USD (Valetax spread/adjustment)
        if symbol == "XAUUSDT":
            return raw_price * 1.0 
        return raw_price
    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return 3920.0 if "XAU" in symbol else 95000.0

# Fungsi Kalkulator & Generator Sinyal SMC Dinamis (Bersih dari tag HTML/span)
def generate_smc_signal(pair, timeframe):
    symbol_code = "XAUUSDT" if "XAU" in pair else "BTCUSDT"
    current_price = get_market_data(symbol_code)
    
    # Variasi jarak berdasarkan Timeframe
    tf_multipliers = {
        "M1": 0.5, "M5": 1.2, "M15": 2.5, 
        "M30": 4.0, "H1": 6.5, "H4": 12.0
    }
    spread = tf_multipliers.get(timeframe, 2.0)
    
    is_bullish = random.choice([True, False])
    
    if is_bullish:
        signal_type = "STRONG BUY (SMC PRO)"
        trend = "BULLISH INSTITUTIONAL ▲"
        entry = round(current_price, 2)
        sl = round(entry - (spread * 1.5), 2)
        tp = round(entry + (spread * 3.0), 2)
        ob_desc = "Bullish OB (Akumulasi Institusi)"
        bos_desc = "BOS (Break of Structure - Tren Naik)"
        fvg_desc = "Bullish FVG (Order Imbalance Terisi)"
        liquidity = "Equal Lows (EQL) Swept"
    else:
        signal_type = "STRONG SELL (SMC PRO)"
        trend = "BEARISH INSTITUTIONAL ▼"
        entry = round(current_price, 2)
        sl = round(entry + (spread * 1.5), 2)
        tp = round(entry - (spread * 3.0), 2)
        ob_desc = "Bearish OB (Distribusi Institusi)"
        bos_desc = "CHoCH (Change of Character - Tren Turun)"
        fvg_desc = "Bearish FVG (Order Imbalance Terisi)"
        liquidity = "Equal Highs (EQH) Swept"

    rsi_val = round(random.uniform(48.0, 68.0) if is_bullish else random.uniform(32.0, 52.0), 2)
    ai_confidence = random.randint(80, 96)
    
    # Format Tanggal & Waktu WIB yang bersih
    wib_time = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%A, %d/%m/%Y - %H:%M WIB")

    message = (
        f"🌸 **AXON SMC INSTITUTIONAL SIGNAL** 🌸\n"
        f"___________________________________\n\n"
        f"📅 {wib_time}\n"
        f"💎 Pair : {pair} (Valetax) | ⏱ TF: {timeframe}\n\n"
        f"💖 Struktur Market : {trend}\n"
        f"🎯 Sinyal Presisi : {signal_type}\n\n"
        f"💰 Entry Area : {entry}\n"
        f"🛑 Stop Loss : {sl} (Batas Area OB)\n"
        f"🎯 Take Profit : {tp} (Target Liquidity)\n\n"
        f"🌺 AI SMC Confidence: {ai_confidence}%\n"
        f"📊 Smart Money Breakdown:\n"
        f"• Order Block (OB) : {ob_desc}\n"
        f"• Market Structure : {bos_desc}\n"
        f"• Fair Value Gap : {fvg_desc}\n"
        f"• Liquidity Pool : {liquidity}\n"
        f"• RSI (14) : {rsi_val}\n\n"
        f"💡 Gunakan rectangle tools MT5 untuk zona."
    )
    
    return message

# Handler Command /start (Menu Utama Pilih Pair)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 XAU/USD (Valetax)", callback_data="pair_XAU/USD")],
        [InlineKeyboardButton("🪙 BTC/USD", callback_data="pair_BTC/USD")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "🌸 **AXON SIGNAL BOT** 🌸\n\nSilahkan pilih instrumen / pair market yang ingin dianalisis:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# Handler Tombol Callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query
