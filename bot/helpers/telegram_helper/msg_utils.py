from bot import ID_CHAT_POSTS, LOGGER, upd_dis
from telegram import InputFile, InlineKeyboardMarkup
from telegram.message import Message
from telegram.update import Update
from telegram.error import TelegramError


def delete_message(message: Message) -> bool:
    try:
        return upd_dis.upd_dis.bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id
        )
    except TelegramError as e:
        LOGGER.error(str(e))
    return False


def send_message(text: str, update: Update, parse_mode="HTML"):
    if not update.message:
        ch = ID_CHAT_POSTS
    else:
        ch = update.message.chat_id
    try:
        return upd_dis.bot.send_message(
            chat_id=ch,
            # reply_to_message_id=update.message.message_id,
            text=text,
            allow_sending_without_reply=True,
            parse_mode=parse_mode,
            disable_web_page_preview=True,
        )
    except TelegramError as e:
        LOGGER.error(str(e))


def edit_message(text: str, message: Message, reply_markup=None):
    try:
        upd_dis.bot.edit_message_text(
            text=text,
            message_id=message.message_id,
            chat_id=message.chat.id,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
    except TelegramError as e:
        LOGGER.error(str(e))


def send_file(file_path, update: Update):
    try:
        with open(file_path, "rb") as f:
            input_file = InputFile(f)
            upd_dis.bot.send_document(
                chat_id=update.message.chat_id, document=input_file, filename=f.name
            )
    except TelegramError as e:
        LOGGER.error(f"Error al enviar documento: {str(e)}")


def send_photo(
    file_path,
    update: Update,
    text: str = "",
    reply=False,
    parse_mode="HTML",
    reply_markup=None,
):
    print(file_path)
    args = {
        "chat_id": ID_CHAT_POSTS,
        "caption": text,
        "parse_mode": parse_mode,
        "allow_sending_without_reply": True,
        "reply_markup": reply_markup,
    }
    if reply:
        args["reply_to_message_id"] = update.message.message_id
    try:
        with open(file_path, "rb") as f:
            input_file = InputFile(f)
            args["photo"] = input_file
            return upd_dis.bot.send_photo(**args)
    except TelegramError as e:
        LOGGER.error(f"Error al enviar foto: {e}")


# def edit_message


def sendMarkup(
    file_path, text: str, update: Update, reply_markup: InlineKeyboardMarkup
):
    # return upd_dis.bot.send_message(update.message.chat_id,
    #                         reply_to_message_id=update.message.message_id,
    #                         text=text,
    #                         reply_markup=reply_markup,
    #                         allow_sending_without_reply=True,

    #                         parse_mode='HTMl')
    return send_photo(file_path, update, text, True, "HTML", reply_markup)


# def sendFile(bot, update: Update, file):
#     with open(file, 'rb') as f:
#         return upd_dis.bot.send_document(
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
#         return upd_dis.bot.send_message(message.chat_id,
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
#         upd_dis.bot.edit_message_text(
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
