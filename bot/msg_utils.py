import telegram
from bot import ID_CHAT, ID_CHAT_POSTS, LOGGER
from telegram import InputFile
from telegram.message import Message
from telegram.update import Update

def deleteMessage(bot, message: Message):
    try:
        bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id)
    except Exception as e:
        LOGGER.error(str(e))

def sendMessage(text: str, bot, update: Update, parse_mode='HTMl'):
    try:
        return bot.send_message(
            update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text=text,
            allow_sending_without_reply=True,
            parse_mode=parse_mode)
    except Exception as e:
        LOGGER.error(str(e))

# def editMessage(text: str, message: Message, reply_markup=None):
#     try:
#         bot.edit_message_text(text=text, message_id=message.message_id,
#                               chat_id=message.chat.id,reply_markup=reply_markup,
#                               parse_mode='HTMl')
#     except Exception as e:
#         LOGGER.error(str(e))

def sendFile(file, bot, update: Update):
    # Abrir el archivo
    with open(file, 'rb') as f:
        input_file = InputFile(f)
    try:
        return bot.send_document(
            chat_id=ID_CHAT,
            document=input_file,
            filename=f.name,
            # chat_id=update.message.chat_id
            )
    except telegram.error.TelegramError as e:
        print(f"Error al enviar documento: {e}")

def sendPhoto(file, bot, text: str='', parse_mode='HTMl'):
    # Abrir el archivo
    with open(file, 'rb') as f:
        input_file = InputFile(f)
        # Enviar archivo al chat
    try:
        return bot.send_photo(
            chat_id=ID_CHAT_POSTS,
            photo=input_file,
            caption=text,
            parse_mode=parse_mode)
        # updater.bot.send_document(chat_id=ID, document=input_file)
    except telegram.error.TelegramError as e:
        print(f"Error al enviar documento: {e}")

# def sendFile(bot, update: Update, file):
#     with open(file, 'rb') as f:
#         return bot.send_document(
#             document=f,
#             filename=f.name,
#             reply_to_message_id=update.message.message_id,
#             chat_id=update.message.chat_id)


# from bot import LOGGER, bot
# from telegram.message import Message
# from telegram.update import Update
# from telegram.error import RetryAfter
# from time import sleep
# def sendMessage(text: str, bot, message: Message):
#     try:
#         return bot.send_message(message.chat_id,
#                             reply_to_message_id=message.message_id,
#                             text=text, allow_sending_without_reply=True, parse_mode='HTMl', disable_web_page_preview=True)
#     except RetryAfter as r:
#         LOGGER.warning(str(r))
#         sleep(r.retry_after * 1.5)
#         return sendMessage(text, bot, message)
#     except Exception as e:
#         LOGGER.error(str(e))
#         return

# def editMessage(text: str, message: Message, reply_markup=None):
#     try:
#         bot.edit_message_text(
#             text=text,
#             message_id=message.message_id,
#             chat_id=message.chat.id,
#             reply_markup=reply_markup,
#             parse_mode='HTMl',
#             disable_web_page_preview=True)
#     # except RetryAfter as r:
#     #     LOGGER.warning(str(r))
#     #     sleep(r.retry_after * 1.5)
#     #     return editMessage(text, message, reply_markup)
#     except Exception as e:
#         LOGGER.error(str(e))
#         return