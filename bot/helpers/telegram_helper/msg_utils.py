import telegram
from bot import ID_CHAT, ID_CHAT_POSTS, LOGGER, bot
from telegram import InputFile
from telegram.message import Message
from telegram.update import Update

def delete_message(message: Message):
    try:
        bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    except telegram.error.TelegramError as e:
        LOGGER.error(str(e))

def send_message(text: str, update: Update, parse_mode='HTML'):
    try:
        return bot.send_message(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text=text,
            allow_sending_without_reply=True,
            parse_mode=parse_mode,
            disable_web_page_preview=True
        )
    except telegram.error.TelegramError as e:
        LOGGER.error(str(e))

def edit_message(text: str, message: Message, reply_markup=None):
    try:
        bot.edit_message_text(
            text=text,
            message_id=message.message_id,
            chat_id=message.chat.id,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except telegram.error.TelegramError as e:
        LOGGER.error(str(e))

def send_file(file_path, update: Update):
    try:
        with open(file_path, 'rb') as f:
            input_file = InputFile(f)
            bot.send_document(
                chat_id=update.message.chat_id,
                document=input_file,
                filename=f.name
            )
    except telegram.error.TelegramError as e:
        LOGGER.error(f"Error al enviar documento: {e}")

def send_photo(file_path, update: Update, text: str = '', parse_mode='HTML'):
    try:
        with open(file_path, 'rb') as f:
            input_file = InputFile(f)
            return bot.send_photo(
                chat_id=ID_CHAT_POSTS,
                photo=input_file,
                # reply_to_message_id=update.message.message_id,
                caption=text,
                parse_mode=parse_mode
            )
    except telegram.error.TelegramError as e:
        LOGGER.error(f"Error al enviar foto: {e}")
        
def send_photo_and_reply(file_path, update: Update, text: str = '', parse_mode='HTML'):
    try:
        with open(file_path, 'rb') as f:
            input_file = InputFile(f)
            return bot.send_photo(
                chat_id=update.message.chat_id,
                photo=input_file,
                reply_to_message_id=update.message.message_id,
                caption=text,
                parse_mode=parse_mode
            )
    except telegram.error.TelegramError as e:
        LOGGER.error(f"Error al enviar foto: {e}")


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