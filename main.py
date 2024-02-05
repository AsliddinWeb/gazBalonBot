# Global requirements
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import logging

from datetime import timedelta, datetime

# Local requirements
from settings import BOT_TOKEN, ADMIN_ID
from api import (get_gazbalon_data, order_create, gazbalon_add_new_last_data,
                 SITE_URL, get_last_order, get_gazbalon_id)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('user_data', None):
        await update.message.reply_html(
            text=f"👋 Hayrli kun <b>{context.user_data['user_data']['name']}</b>!\n"
                 f"🕘 Siz oxirgi marta <b>{context.user_data['user_data']['last_status']}</b> da ariza yuborgansiz!",
            reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("☑️ Murojaat yuborish"), KeyboardButton("♻️ Murojaat xolati")]
                    ], resize_keyboard=True)
        )
        context.user_data['state'] = 'CABINET'
    else:
        await update.message.reply_html(
            text=f'👋 Assalom aleykum <b>@{context.bot.username}</b> ga hush kelibsiz!\n\n'
                 f'🆔 ID karta raqamingizni <b>12345678</b> ko\'rinishida kiriting!',
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['state'] = 'HOME'

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('state') == 'HOME':
        gazbalon_id = update.message.text

        if gazbalon_id.isdigit():
            data = await get_gazbalon_data(gazbalon_id)

            if data.get('status_code') == 200:
                context.user_data['user_data'] = data.get('data')
                await update.message.reply_html(
                    text=f"👋 Hayrli kun <b>{context.user_data['user_data']['name']}</b>!\n"
                         f"🕘 Siz oxirgi marta <b>{context.user_data['user_data']['last_status']}</b> da ariza yuborgansiz!",
                    reply_markup=ReplyKeyboardMarkup([
                        [KeyboardButton("☑️ Murojaat yuborish"), KeyboardButton("♻️ Murojaat xolati")]
                    ], resize_keyboard=True)
                )
                context.user_data['state'] = 'CABINET'
            else:
                await update.message.reply_html(
                    text=f"❌ Bu ID raqam orqali karta ma'lumotlari topilmadi!\n\n"
                         f"👉 <b>Tekshirib qaytadan yuboring...</b>"
                )
        else:
            await update.message.reply_html(
                text=f"🆔 ID karta raqamingizni namuna bo'yicha kiriting..."
            )
    elif context.user_data.get('state') == 'CABINET':
        if update.message.text == "☑️ Murojaat yuborish":
            data = await get_gazbalon_data(context.user_data.get('user_data')['gazbalon_id'])
            context.user_data['user_data'] = data.get('data')

            last_status_data = context.user_data.get('user_data')['last_status']

            if last_status_data is None:
                print(True)
                data = await order_create(context.user_data.get('user_data')['id'], update.effective_user.id)
                today = datetime.now()

                if data['status_code'] == 201:
                    new_data = await gazbalon_add_new_last_data(context.user_data.get('user_data')['gazbalon_id'], today.date())
                    data = await get_gazbalon_data(context.user_data.get('user_data')['gazbalon_id'])
                    context.user_data['user_data'] = data.get('data')
                    await update.message.reply_html(
                        text=f"✅ <b>Tabriklaymiz arizangiz muvaffaqqiyatli yuborildi!</b>\n"
                             f"🆔 ID: <b>{data['data']['id']}</b>"
                    )

                    await context.bot.sendMessage(
                        chat_id=ADMIN_ID,
                        text=f"<b>❇️ Yangi ariza:\n\n"
                             f"👨‍🔧 Ism:</b> {context.user_data['user_data']['name']}\n"
                             f"👉 <b>Batafsil:</b> {SITE_URL}gaz_app/order/{data['data']['id']}/",
                        parse_mode="HTML"
                    )
            else:
                if last_status_data:
                    last_status = datetime.strptime(last_status_data, "%Y-%m-%d")
                else:
                    last_status = datetime.now().date()

                # Today
                today = datetime.now()

                # Interval
                interval = last_status + timedelta(days=30)

                if interval < today:
                    print(True)
                    data = await order_create(context.user_data.get('user_data')['id'], update.effective_user.id)

                    if data['status_code'] == 201:
                        new_data = await gazbalon_add_new_last_data(context.user_data.get('user_data')['gazbalon_id'], today.date())
                        data = await get_gazbalon_data(context.user_data.get('user_data')['gazbalon_id'])
                        context.user_data['user_data'] = data.get('data')
                        await update.message.reply_html(
                            text=f"✅ <b>Tabriklaymiz arizangiz muvaffaqqiyatli yuborildi!</b>\n"
                                 f"🆔 ID: <b>{data['data']['id']}</b>"
                        )

                        await context.bot.sendMessage(
                            chat_id=ADMIN_ID,
                            text=f"<b>❇️ Yangi ariza:\n\n"
                                 f"👨‍🔧 Ism:</b> {context.user_data['user_data']['name']}\n"
                                 f"👉 <b>Batafsil:</b> {SITE_URL}gaz_app/order/{data['data']['id']}/",
                            parse_mode="HTML"
                        )

                else:
                    await update.message.reply_html(
                        text=f"<b>Ariza yuborish amalga oshirilmadi!</b>\n\n"
                             f"Siz <b>{context.user_data['user_data']['last_status']}</b> da ariza yuborgansiz!"
                    )
        elif update.message.text == "♻️ Murojaat xolati":
            last_order = await get_last_order(context.user_data['user_data']['gazbalon_id'])
            gazbalon = await get_gazbalon_id(last_order['data']['gazbalon'])
            if last_order['status_code'] == 200:
                await update.message.reply_html(
                    text=f"<b>♻️ Oxirgi murojaatingiz xolati!</b>\n\n"
                         f"🆔Murojaat ID: {last_order['data']['id']}\n"
                         f"🧍‍♂ Murojatchi: {gazbalon['data']['name']}\n"
                         f"📍 Manzil: {gazbalon['data']['address']}\n"
                         f"📅 Yuborilgan vaqt: {datetime.fromisoformat(last_order['data']['created_at']).strftime("%Y-%m-%d %H:%M:%S")} da\n\n"
                         f"🔹 Murojaat xolati: <b>{last_order['data']['ariza_xolati']}</b>."
                )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start_handler))
app.add_handler(MessageHandler(filters.TEXT, message_handler))

app.run_polling()