import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# --- НАЛАШТУВАННЯ ---
API_TOKEN = '7306969241:AAEwJXOsKikKMN7MA2LNRFv57ADmM_lKf0U'
ADMIN_IDS = [6867625126, 5506402566] 
PROJECT_NAME = "Ukraine Legacy"
WEBSITE_URL = "https://ukrainelegacy.netlify.app/"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- КЛАВІАТУРИ ---

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Як почати грати", callback_data="u_how")],
        [InlineKeyboardButton(text="💎 Проблеми з донатом", callback_data="u_donate")],
        [InlineKeyboardButton(text="🛠 Технічна допомога", callback_data="u_tech")],
        [InlineKeyboardButton(text="🆘 Зв'язок з Адміністрацією", callback_data="u_admin")],
        [InlineKeyboardButton(text="🌐 Наш сайт", url=WEBSITE_URL)]
    ])

def get_admin_kb(user_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ ВІДПОВІСТИ (REPLY)", callback_data=f"hint_{user_id}")],
        [InlineKeyboardButton(text="✅ ЗАКРИТИ ТИКЕТ", callback_data=f"close_{user_id}")]
    ])

# --- ЛОГІКА МЕНЮ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 **Вітаємо у техпідтримці {PROJECT_NAME}!**\n\n"
        "Оберіть категорію, яка вас цікавить, або напишіть нам напряму:",
        reply_markup=get_main_kb(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("u_"))
async def menu_handler(callback: CallbackQuery):
    if callback.data == "u_how":
        await callback.message.answer(f"🚀 **Інструкція:**\n1. Сайт: {WEBSITE_URL}\n2. Скачайте лаунчер.\n3. Встановіть гру.")
    elif callback.data == "u_admin":
        await callback.message.answer("📝 **Напишіть ваше запитання одним повідомленням.**\nАдміністрація отримає його миттєво.")
    await callback.answer()

# --- АДМІН-ФУНКЦІЇ ---

@dp.callback_query(F.data.startswith("hint_"))
async def hint_handler(callback: CallbackQuery):
    await callback.answer("Щоб відповісти, натисніть 'REPLY' на повідомлення вище!", show_alert=True)

@dp.callback_query(F.data.startswith("close_"))
async def close_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    try:
        await bot.send_message(user_id, f"✅ **Ваше звернення було закрите.**\nДякуємо за гру на {PROJECT_NAME}!")
        await callback.message.edit_text(callback.message.text + "\n\n🛑 **СТАТУС: ТИКЕТ ЗАКРИТО**")
        await callback.answer("Закрито!")
    except:
        await callback.answer("Помилка при закритті")

# --- ГОЛОВНИЙ ОБРОБНИК (ULTRA LOGIC) ---

@dp.message()
async def global_handler(message: types.Message):
    # ПЕРЕВІРКА: ЧИ ПИШЕ АДМІН (ВІДПОВІДЬ ГРАВЦЕВІ)
    if message.from_user.id in ADMIN_IDS:
        if message.reply_to_message:
            content = message.reply_to_message.text or message.reply_to_message.caption or ""
            # Пошук ID за допомогою регулярного виразу
            found_id = re.search(r"ID: (\d+)", content)
            
            if found_id:
                user_id = int(found_id.group(1))
                try:
                    if message.text:
                        await bot.send_message(user_id, f"⚠️ **Відповідь від Адміністрації {PROJECT_NAME}:**\n\n{message.text}")
                    elif message.photo:
                        await bot.send_photo(user_id, message.photo[-1].file_id, caption=f"⚠️ **Відповідь від Адміністрації {PROJECT_NAME}**")
                    
                    await message.reply(f"✅ **Надіслано гравцеві (ID: {user_id})**", reply_markup=get_admin_kb(user_id))
                except Exception as e:
                    await message.reply(f"❌ Помилка надсилання: {e}")
            else:
                await message.reply("❌ **Помилка:** Я не знайшов ID гравця. Відповідайте (Reply) саме на повідомлення бота з даними тикета.")
        return

    # ПЕРЕВІРКА: ЧИ ПИШЕ ГРАВЕЦЬ (СТВОРЕННЯ ТИКЕТА)
    ticket_template = (
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"📩 **НОВИЙ ТИКЕТ {PROJECT_NAME}**\n"
        f"👤 Від: @{message.from_user.username or 'NoUser'}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"➖➖➖➖➖➖➖➖➖➖"
    )

    for admin_id in ADMIN_IDS:
        try:
            if message.text:
                await bot.send_message(admin_id, f"{ticket_template}\n\n📝 **Текст:** {message.text}", reply_markup=get_admin_kb(message.from_user.id))
            elif message.photo:
                await bot.send_photo(admin_id, message.photo[-1].file_id, caption=f"{ticket_template}\n\n🖼 **Дивіться скріншот вище**", reply_markup=get_admin_kb(message.from_user.id))
        except:
            continue
    
    await message.reply("✅ **Ваше звернення надіслано!**\nОчікуйте на відповідь адміністратора.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print(f"ULTIMATE {PROJECT_NAME} SUPPORT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
