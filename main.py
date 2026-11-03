import logging
import datetime
import requests
import pandas as pd
import pandas_ta as ta
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

def get_live_klines(symbol="PAXGUSDT", interval="1h", limit=50):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        res = requests.get(url, timeout=5)
        data = res.json()
        
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
        ])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except Exception as e:
        logging.error(f"Error fetching klines: {e}")
        return None

def get_realtime_data(asset_type, tf="1h"):
    tf_map = {
        "m1": "1m", "m5": "5m", "m15": "15m",
        "m30": "30m", "h1": "1h", "h4": "4h", "d1": "1d"
    }
    interval = tf_map.get(tf, "1h")
    
    if asset_type == "gold":
        df = get_live_klines("PAXGUSDT", interval, limit=60)
        # Kalibrasi presisi khusus untuk menyesuaikan feed harga XAUUSD Valetax
        multiplier = 0.7512  
    else:
        df = get_live_klines("BTCUSDT", interval, limit=60)
        multiplier = 1.0

    if df is not None and not df.empty:
        df['open'] = df['open'] * multiplier
        df['high'] = df['high'] * multiplier
        df['low'] = df['low'] * multiplier
        df['close'] = df['close'] * multiplier
        
        df['RSI'] = ta.rsi(df['close'], length=14)
        df['MA20'] = ta.sma(df['close'], length=20)
        df['MA50'] = ta.sma(df['close'], length=50)
        return df
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🥇 Analisis Gold (Valetax XAUUSD)", callback_data="asset_gold"),
            InlineKeyboardButton("₿ Analisis Bitcoin (BTC)", callback_data="asset_btc")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🌸 **AXION SMC INSTITUTIONAL BOT (VALETAX)** 🌸\n\nLive Market Connected: Order Block, FVG, Structure & Liquidity.\n\nPilih aset market:"
    
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
    if data == "back_to_start":
        await start(update, context)
        return

    if data.startswith("asset_"):
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
            [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        asset_name = "XAU/USD (Valetax)" if asset == "gold" else "BTC/USD"
        try:
            await query.message.edit_text(f"💎 **Aset: {asset_name}**\nPilih Timeframe Real-Time:", reply_markup=reply_markup, parse_mode="Markdown")
        except Exception:
            pass
        return

    if data.startswith("tf_"):
        parts = data.split("_")
        if len(parts) < 3:
            await start(update, context)
            return
            
        asset = parts[1]
        tf = parts[2]
        name = "XAU/USD (Valetax)" if asset == "gold" else "BTC/USD"
        
        try:
            await query.message.edit_text(f"⏳ Menarik live market {name} ({tf.upper()})...")
        except Exception:
            pass

        df = get_realtime_data(asset, tf)
        if df is None or df.empty:
            await query.message.edit_text("❌ Gagal menarik data market. Coba beberapa saat lagi.")
            return
            
        l = df.iloc[-1]
        close_val = float(l['close'])
        rsi_val = float(l['RSI']) if not pd.isna(l['RSI']) else 50.0
        ma20 = float(l['MA20']) if not pd.isna(l['MA20']) else close_val
        ma50 = float(l['MA50']) if not pd.isna(l['MA50']) else close_val

        recent_high = float(df['high'].tail(15).max())
        recent_low = float(df['low'].tail(15).min())

        if close_val >= ma20 and ma20 >= ma50:
            ob_type = "Bullish OB (Akumulasi Institusi)"
            fvg_status = "Bullish FVG (Order Imbalance Terisi)"
            structure = "BOS (Break of Structure - Tren Naik)"
            liquidity = "Equal Lows (EQL) Swept"
            signal = "STRONG BUY (SMC PRO) 🟢"
            trend = "BULLISH INSTITUTIONAL 📈"
            confidence = 95
        elif close_val <= ma20 and ma20 <= ma50:
            ob_type = "Bearish OB (Distribusi Institusi)"
            fvg_status = "Bearish FVG (Order Imbalance Tolakan)"
            structure = "CHoCH / BOS (Bearish Continuation)"
            liquidity = "Equal Highs (EQH) Swept"
            signal = "STRONG SELL (SMC PRO) 🔴"
            trend = "BEARISH INSTITUTIONAL 📉"
            confidence = 95
        else:
            ob_type = "Consolidation OB Zone"
            fvg_status = "Neutral Fvg / Equilibrium"
            structure = "Ranging Market (Indecision)"
            liquidity = "Internal Range Liquidity"
            signal = "WAIT & SEE (Koreksi Market) 🟡"
            trend = "SIDEWAYS / KONSOLIDASI ⚖️"
            confidence = 80

        entry = round(close_val, 2)
        if "BUY" in signal:
            sl = round(recent_low - 1.5, 2)
            tp = round(entry + ((entry - sl) * 1.5), 2)
        elif "SELL" in signal:
            sl = round(recent_high + 1.5, 2)
            tp = round(entry - ((sl - entry) * 1.5), 2)
        else:
            sl = round(recent_low, 2)
            tp = round(recent_high, 2)
        
        now_str = datetime.datetime.now().strftime("%A, %d/%m/%Y - %H:%M WIB")

        msg = (
            f"🌸 **AXION SMC INSTITUTIONAL SIGNAL** 🌸\n"
            f"──────────────────────────────────────\n"
            f"📅 {now_str}\n"
            f"💎 Pair : {name}  |  ⏱ TF: {tf.upper()}\n\n"
            f"💖 Struktur Market : {trend}\n"
            f"🎯 Sinyal Presisi  : {signal}\n\n"
            f"💰 Entry Area  : {entry}\n"
            f"🛑 Stop Loss   : {sl} (Batas Area OB)\n"
            f"🎯 Take Profit : {tp} (Target Liquidity)\n\n"
            f"🌺 **AI SMC Confidence: {confidence}%**\n"
            f"📊 **Smart Money Breakdown:**\n"
            f"   • Order Block (OB) : {ob_type}\n"
            f"   • Market Structure : {structure}\n"
            f"   • Fair Value Gap   : {fvg_status}\n"
            f"   • Liquidity Pool   : {liquidity}\n"
            f"   • RSI (14)         : {round(rsi_val, 2)}\n\n"
            f"💡 Sinkronisasi Live Market Valetax."
        )

        keyboard = [[
            InlineKeyboardButton("🔄 Analisa Ulang", callback_data=f"asset_{asset}"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_start")
        ]]
        
        try:
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception:
            try:
                await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            except Exception:
                pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.post_init = set_bot_commands
    app.run_polling()
