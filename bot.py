import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ContextTypes

# Ваш токен, полученный от BotFather
TOKEN = '6696595340:AAErvLKqiLR4wAmbGLB0r_cP7ODlAg4e7kk'
CHANNEL_ID = '@ishutebyatverr'
YOUR_ADMIN_CHAT_ID = '1615873144'

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Хранение информации о сообщениях (фотографии и тексты)
message_storage = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Отправьте мне новость, и я передам её администратору для проверки.')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_id = update.message.message_id
    message_text = update.message.text
    username = update.message.from_user.username or "No Username"  # Получаем username отправителя
    
    # Сохраняем текст сообщения и username
    message_storage[message_id] = {'text': message_text, 'username': username}

    # Отправляем администратору текст с кнопками "Анонимно" и "Не Анонимно"
    keyboard = [
        [
            InlineKeyboardButton("Не Анонимно", callback_data=f"publish_non_anonymous:{message_id}"),
            InlineKeyboardButton("Анонимно", callback_data=f"publish_anonymous:{message_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=YOUR_ADMIN_CHAT_ID, text=f"Новость от пользователя: {message_text}", reply_markup=reply_markup)

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_id = update.message.message_id
    photo_file_id = update.message.photo[-1].file_id  # Получаем файл ID самой большой фотографии
    caption = update.message.caption or ""  # Получаем подпись, если она есть
    username = update.message.from_user.username or "No Username"  # Получаем username отправителя

    # Сохраняем фото, подпись и username
    message_storage[message_id] = {'photo_file_id': photo_file_id, 'caption': caption, 'username': username}

    # Отправляем администратору фотографию с кнопками "Анонимно" и "Не Анонимно"
    keyboard = [
        [
            InlineKeyboardButton("Не Анонимно", callback_data=f"publish_non_anonymous:{message_id}"),
            InlineKeyboardButton("Анонимно", callback_data=f"publish_anonymous:{message_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(chat_id=YOUR_ADMIN_CHAT_ID, photo=photo_file_id, caption=f"Фото от пользователя: {caption}", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("publish_non_anonymous:"):
        message_id = int(data.split(":")[1])
        message_info = message_storage.get(message_id)
        
        if message_info:
            username = message_info.get('username', "No Username")
            if 'text' in message_info:
                message_text = message_info['text']
                await context.bot.send_message(chat_id=CHANNEL_ID, text=f"Новость от @{username}: {message_text}")
            elif 'photo_file_id' in message_info:
                photo_file_id = message_info['photo_file_id']
                caption = message_info.get('caption', '')
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file_id, caption=f"@{username}: {caption}")

            # Удаляем кнопки после публикации
            await query.edit_message_reply_markup(reply_markup=None)
        else:
            await query.edit_message_text(text="Ошибка: информация не найдена.")

    elif data.startswith("publish_anonymous:"):
        message_id = int(data.split(":")[1])
        message_info = message_storage.get(message_id)
        
        if message_info:
            if 'text' in message_info:
                message_text = message_info['text']
                await context.bot.send_message(chat_id=CHANNEL_ID, text=message_text)
            elif 'photo_file_id' in message_info:
                photo_file_id = message_info['photo_file_id']
                caption = message_info.get('caption', '')
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file_id, caption=caption)

            # Удаляем кнопки после публикации
            await query.edit_message_reply_markup(reply_markup=None)
        else:
            await query.edit_message_text(text="Ошибка: информация не найдена.")

def main() -> None:
    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
