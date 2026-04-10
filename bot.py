#!/usr/bin/env python3
import os
import sys
import io
import time
import base64
import logging

from PIL import Image
from dotenv import load_dotenv
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.tokenmix.ai/v1")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

log = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

# per-user state (in-memory, resets on restart)
histories = {}
user_models = {}


def allowed(uid):
    if not ALLOWED_USERS:
        return True
    ids = [int(x.strip()) for x in ALLOWED_USERS.split(",") if x.strip()]
    return uid in ids


def get_hist(uid):
    if uid not in histories:
        histories[uid] = []
    return histories[uid]


async def stream_reply(msg, messages, model):
    """Stream LLM response, editing the telegram message as chunks arrive."""
    full = ""
    last_len = 0
    last_t = time.time()

    try:
        stream = await client.chat.completions.create(
            model=model, messages=messages, stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content

            now = time.time()
            if full and (now - last_t > 1.0 or len(full) - last_len > 80):
                try:
                    preview = full[:4000] + "..." if len(full) > 4000 else full + " ▌"
                    await msg.edit_text(preview)
                except Exception:
                    pass
                last_t = now
                last_len = len(full)

    except Exception as e:
        err = str(e)
        if "401" in err or "403" in err or "Incorrect API key" in err:
            await msg.edit_text(
                "Error: Authentication failed — check API_KEY in .env\n"
                "Get a key at https://tokenmix.ai ($1 free credit)"
            )
        elif "429" in err:
            await msg.edit_text("Rate limited — wait a moment and try again.")
        else:
            await msg.edit_text(f"API error: {err[:300]}")
        return None

    if not full:
        await msg.edit_text("(empty response)")
        return None

    try:
        await msg.edit_text(full[:4096])
    except Exception:
        pass
    return full


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a message and I'll reply using AI.\n"
        "Send a photo with a caption to ask about images.\n\n"
        "/model <name> — switch model\n"
        "/clear — reset conversation\n"
        "/help — show this"
    )


async def cmd_model(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split(maxsplit=1)
    uid = update.effective_user.id
    if len(parts) < 2:
        cur = user_models.get(uid, MODEL)
        await update.message.reply_text(f"Current: {cur}\nUsage: /model gpt-4o")
        return
    name = parts[1].strip()
    user_models[uid] = name
    await update.message.reply_text(f"Switched to {name}")


async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    histories[update.effective_user.id] = []
    await update.message.reply_text("Conversation cleared.")


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not allowed(uid):
        return

    hist = get_hist(uid)
    hist.append({"role": "user", "content": update.message.text})

    while len(hist) > MAX_HISTORY:
        hist.pop(0)

    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + hist
    model = user_models.get(uid, MODEL)

    placeholder = await update.message.reply_text("...")
    reply = await stream_reply(placeholder, msgs, model)
    if reply:
        hist.append({"role": "assistant", "content": reply})


async def on_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    log.info("photo from %s, caption=%s", uid, update.message.caption)
    if not allowed(uid):
        return

    caption = update.message.caption or "What's in this image?"

    try:
        # photos sent as "photo" (compressed) or as "document" (file)
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await ctx.bot.get_file(photo.file_id)
        elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("image/"):
            file = await ctx.bot.get_file(update.message.document.file_id)
        else:
            return
        raw = await file.download_as_bytearray()
        # resize to keep API requests small
        img = Image.open(io.BytesIO(raw))
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        b64 = base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        log.error("failed to process photo: %s", e)
        await update.message.reply_text("Couldn't process the image. Try again?")
        return

    vision_msg = {
        "role": "user",
        "content": [
            {"type": "text", "text": caption},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ],
    }

    hist = get_hist(uid)
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + hist + [vision_msg]
    model = user_models.get(uid, MODEL)

    placeholder = await update.message.reply_text("...")
    reply = await stream_reply(placeholder, msgs, model)
    if reply:
        hist.append({"role": "user", "content": f"[photo] {caption}"})
        hist.append({"role": "assistant", "content": reply})


def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not set.")
        print("Get one from @BotFather on Telegram, then add it to .env")
        sys.exit(1)

    if not API_KEY:
        print("Error: API key not configured.")
        print("")
        print("To get started:")
        print("  1. Get a free API key at https://tokenmix.ai ($1 free credit)")
        print("     Or use any OpenAI-compatible API provider")
        print("  2. Set API_KEY in .env")
        sys.exit(1)

    logging.basicConfig(
        format="%(asctime)s [%(name)s] %(message)s",
        level=logging.INFO,
    )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("model", cmd_model))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.PHOTO | (filters.Document.IMAGE), on_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    async def on_error(update, ctx):
        log.error("unhandled error: %s", ctx.error, exc_info=ctx.error)

    app.add_error_handler(on_error)

    log.info("bot started — model=%s", MODEL)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
