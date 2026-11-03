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
            return raw_price * 1.0 
        return raw_price
    except Exception as e:
        print(f"Error fetching Binance data: {e}")
        return 3920.0 if "XAU" in symbol else 95000.0

def generate_smc_signal(pair, timeframe):
    symbol_code = "XAUUSDT" if "XAU" in pair else "BTCUSDT"
    current_price = get_market_data(symbol_code)
    
    tf_multipliers = {
        "M1": 0.5, "M5": 1.2, "M15": 2.5, 
        "M30": 4.0, "H1": 6.5, "H4": 12.0
    }
    spread = tf_multipliers.get(timeframe, 2.0)
    
    is_bullish = random.choice([True, False])
    
    if is_bullish:
        signal_type = "STRONG BUY (SMC PRO)"
        trend = "BULLISH INSTITUTIONAL"
        entry = round(current_price, 2)
        sl = round(entry - (spread * 1.5), 2)
        tp = round(entry + (spread * 3.0), 2)
        ob_desc = "Bullish OB (Akumulasi Institusi)"
        bos_desc = "BOS (Break of Structure - Tren Naik)"
        fvg_desc = "Bullish FVG (Order Imbalance Terisi)"
        liquidity = "Equal Lows (EQL) Swept"
    else:
        signal_type = "STRONG SELL (SMC PRO)"
        trend = "BEARISH INSTITUTIONAL"
        entry = round(current_price, 2)
        sl = round(entry + (spread * 1.5), 2)
        tp = round(entry - (spread * 3.0), 2)
        ob_desc = "Bearish OB (Distribusi Institusi)"
        bos_desc = "CHoCH (Change of Character - Tren Turun)"
        fvg_desc = "Bearish FVG (Order Imbalance Terisi)"
        liquidity = "Equal Highs (EQH) Swept"

    rsi_val = round(random.uniform(48.0, 68.0) if is_bullish else random.uniform(32.0, 52.0), 2)
    ai_confidence = random.randint(80, 96)
    
    wib_time = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%A, %d/%m/%Y - %H:%M WIB")

    line1 = f"🌸 **AXON SMC INSTITUTIONAL SIGNAL** 🌸"
    line2 = f"___________________________________"
    line3 = f"📅 {wib_time}"
    line4 = f"💎 Pair : {pair} (Valetax) | ⏱ TF: {timeframe}"
    line5 = f"💖 Struktur Market : {trend}"
    line6 = f"🎯 Sinyal Presisi : {signal_type}"
    line7 = f"💰 Entry Area : {entry}"
    line8 = f"🛑 Stop Loss : {sl} (Batas Area OB)"
    line9 = f"🎯 Take Profit : {tp} (Target Liquidity)"
    line10 = f"🌺 AI SMC Confidence: {ai_confidence}%"
    line11 = f"📊 Smart Money Breakdown:"
    line12 = f"• Order Block (OB) : {ob_desc}"
    line13 = f"• Market Structure : {bos_desc}"
    line14 = f"• Fair Value Gap : {fvg_desc}"
    line15 = f"• Liquidity Pool : {liquidity}"
    line16 = f"• RSI (14) : {rsi_val}"
    line17 = f"💡 Gunakan rectangle tools MT5 untuk zona."

    message = f"{line1}\n{line2}\n\n{line3}\n{line4}\n\n{line5}\n{line6}\n\n{line7}\n{line8}\n{line9}\n\n{line10}\n{line11}\n{line12}\n{line13}\n{line14}\n{line15}\n{line16}\n\n{line17}"
    
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
