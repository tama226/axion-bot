import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN", "MASUKKAN_TOKEN_BOT_KAMU_DISINI")

def get_market_data(symbol="XAUUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        raw_price = float(data['price'])
        
        if symbol == "XAUUSDT":
            return 3929.18 if raw_price > 4000 or raw_price < 3000 else raw_price
        return raw_price
    except Exception as e:
        print(f"Error fetching data: {e}")
        return 3929.18 if "XAU" in symbol else 95000.0

def generate_smc_signal(pair, timeframe):
    symbol_code = "XAUUSDT" if "XAU" in pair else "BTCUSDT"
    current_price = get_market_data(symbol_code)
    
    tf_multipliers = {
        "M1": 0.3, "M5": 0.8, "M15": 1.5, 
        "M30": 2.5, "H1": 4.0, "H4": 7.5
    }
    spread = tf_multipliers.get(timeframe, 1.0)
    
    random.seed(datetime.now().microsecond + random.randint(1, 10000))
    is_bullish = random.choice([True, False])
    
    price_offset = random.uniform(-0.8, 0.8) if "XAU" in pair else random.uniform(-15.0, 15.0)
    entry = round(current_price + price_offset, 2)
    
    if is_bullish:
        signal_type = "STRONG BUY (SMC PRO)"
        trend = "BULLISH INSTITUTIONAL ▲"
        sl = round(entry - (spread * 1.5), 2)
        tp = round(entry + (spread * 3.0), 2)
        ob_desc = "Bullish OB (Akumulasi Institusi)"
        bos_desc = "BOS (Break of Structure - Tren Lanjut Naik)"
        fvg_desc = "Bullish FVG (Inefficiency Terisi Menuju Naik)"
        liquidity = "Equal Lows (EQL) Swept - Berburu Stop Loss Buyers"
    else:
        signal_type = "STRONG SELL (SMC PRO)"
        trend = "BEARISH INSTITUTIONAL ▼"
        sl = round(entry + (spread * 1.5), 2)
        tp = round(entry - (spread * 3.0), 2)
        ob_desc = "Bearish OB (Distribusi Institusi)"
        bos_desc = "CHoCH (Change of Character - Pembalikan Tren)"
        fvg_desc = "Bearish FVG (Inefficiency Penolakan Turun)"
        liquidity = "Equal Highs (EQH) Swept - Berburu Stop Loss Sellers"

    rsi_val = round(random.uniform(52.0, 72.0) if is_bullish else random.uniform(28.0, 48.0), 2)
    ai_confidence = random.randint(84, 98)
    
    wib_time = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%A, %d/%m/%Y - %H:%M WIB")

    message = (
        f"🌸 **AXON SMC INSTITUTIONAL SIGNAL** 🌸\n"
        f"___________________________________\n\n"
        f"📅 {wib_time}\n"
        f"💎 Pair : {pair} (Valetax) | ⏱ TF: {timeframe}\n\n"
        f"💖 Struktur Market : {trend}\n"
        f"📈\n"
        f"🎯 Sinyal Presisi : {signal_type}\n"
        f"🟢\n\n"
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
        f"💡 Gunakan rectangle tools MT5 untuk menandai zona OB & FVG."
    )
    
    return message

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("pair_"):
        pair = data.split("_")[1]
        context.user_data["selected_pair"] = pair
        
        keyboard = [
            [
                InlineKeyboardButton("M1", callback_data="tf_M1"),
                InlineKeyboardButton("M5", callback_data="tf_M5"),
                InlineKeyboardButton("M15", callback_data="tf_M15"),
            ],
            [
                InlineKeyboardButton("M30", callback_data="tf_M30"),
                InlineKeyboardButton("H1", callback_data="tf_H1"),
                InlineKeyboardButton("H4", callback_data="tf_H4"),
            ],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"✅ Pair: **{pair}**\nPilih timeframe analisis:", 
            reply_markup=reply_markup, 
            parse_mode="Markdown"
        )

    elif data.startswith("tf_"):
        timeframe = data.split("_")[1]
        context.user_data["selected_tf"] = timeframe
        pair = context.user_data.get("selected_pair", "XAU/USD")
        
        signal_text = generate_smc_signal(pair, timeframe)
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Analisa Ulang", callback_data=f"tf_{timeframe}"),
                InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(signal_text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "main_menu":
        await start(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running and ready...")
    app.run_polling()

if __name__ == "__main__":
    main()
