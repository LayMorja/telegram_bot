import logging as log
# Логирование, отображение взаимодействий бота с сервером
from os import getenv
# Модуль ОС, конкретно здесь для получение данных из вирт. окружения

from aiogram import Bot, types
# Основной класс + типы получаемой информации в чате
from aiogram.contrib.middlewares.logging import LoggingMiddleware
# "Прокаченное логирование"
from aiogram.dispatcher import Dispatcher
# Наблюдатель за изменениями
from aiogram.dispatcher.webhook import SendMessage, SendAudio, SendPhoto, SendVoice, SendSticker
# Функция для действий бота
from aiogram.utils.executor import start_webhook
# Функция для WebHook'a
from aiogram.utils.exceptions import BotBlocked

# Исключения/обработка ошибок

API_TOKEN = getenv('TOKEN')
if not API_TOKEN:
    exit("Ошибка: а токена-то нет!")

# Настройки ВебХука
WEBHOOK_HOST = getenv('HOST').strip()
WEBHOOK_PATH = ''
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Настройки Веб-сервиса
WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = 8000

# Базовая конфигурация + HTML-метод парсинга
log.basicConfig(level=log.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp: Dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Начать приключения"),
        types.BotCommand("help", "Что за приключения?"),
        types.BotCommand("teacher", "Учител"),
    ])


async def on_shutdown(dp: Dispatcher):
    log.warning('Выключаюсь!...')
    await bot.delete_webhook()

    # Закрываем соединение с БД
    # await dp.storage.close()
    # await dp.storage.wait_closed()
    log.warning('Bye!')


# Обработка входящих команд
@dp.message_handler(commands=['start'])
async def echo(message: types.Message):
    await message.reply(f"Добро пожаловать, <strong>{message.from_user.first_name}</strong>!\n"
                        f"Если тебе интересно, можешь заглянуть на мой <a "
                        f"href=\"https://github.com/LayMorja\">GitHub</a>")


@dp.message_handler(commands=['help'])
async def echo(message: types.Message):
    return SendMessage(message.chat.id, 'Вы обратились к справке бота, но здесь, к сожалению, пока ничего нет - '
                                        'этот бот ещё не знает, кем ему быть')


@dp.message_handler(commands=['teacher'])
async def echo(message: types.Message):
    return SendMessage(message.chat.id, 'В создании нашего приключения мне помогал '
                                        '<a href=\"https://github.com/K-Mickey\">Mike</a>')


# Эхо-ответ на сообщение
@dp.message_handler(content_types=types.ContentType.TEXT)
async def echo(message: types.Message):
    await message.answer(f'<s>{message.text}</s>')


# Эхо-ответ на текстовое сообщение
@dp.message_handler(content_types=types.ContentType.TEXT)
async def echo(message: types.Message):
    await message.answer(message.text)


# Эхо-ответ на стикер
@dp.message_handler(content_types=types.ContentType.STICKER)
async def echo_sticker(message: types.Sticker):
    return SendSticker(message['chat']['id'], sticker=message['sticker'].file_id)


# Эхо-ответ на аудио
@dp.message_handler(content_types=types.ContentType.AUDIO)
async def echo_audio(message: types.Audio):
    file = message['audio']['file_id']
    performer = message['audio']['performer']
    title = message['audio']['title']
    await message.answer(f'Трек "{title}" в исполнении "{performer}" шикарен!')
    return SendAudio(chat_id=message['from']['id'], audio=file)


# Эхо-ответ на аудио
@dp.message_handler(content_types=types.ContentType.VOICE)
async def echo_voice(message: types.Voice):
    file = message['voice']['file_id']
    duration = message['voice']['duration']
    text_with = 'Можно и послушать!' if duration < 30 else 'Думаю, тебе будет лень этим заниматься, но держи...'
    await message.reply(text_with)
    return SendVoice(message['chat']['id'], voice=file)


# Эхо-ответ на фотографию
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def echo_photo(message: types.ChatPhoto):
    caption = message['caption'] or None
    file = message['photo'][-1]['file_id']
    return SendPhoto(message['chat']['id'], photo=file, caption=caption)


# Обработка исключений
@dp.errors_handler(exception=BotBlocked)
async def blocked_error(update: types.Update, exception: BotBlocked):
    print(f'Пользователь меня заблокировал! :(\n'
          f'Сообщение: {update}\n'
          f'Ошибка: {exception}\n')
    # Действия при обработке исключения
    return True
    # Выход из функции


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
