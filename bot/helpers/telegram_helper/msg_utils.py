#!/usr/bin/env python

from telegram import InputFile, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from bot import LOGGER

# from bot import ID_CHAT_POSTS, LOGGER, upd_dis
# from telegram import ChatAction, InputFile, InlineKeyboardMarkup
# from telegram.message import Message
# from telegram.update import Update
# from telegram.error import TelegramError
# from typing import Union


async def delete_message(context, message):
    try:
        return await context.bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id
        )
    except TelegramError as e:
        LOGGER.error(str(e))
    except Exception as e:
        LOGGER.error(str(e))
    return False


async def edit_message(context, message, text, reply_markup=None):
    try:
        return await context.bot.edit_message_text(
            text=text,
            message_id=message.message_id,
            chat_id=message.chat.id,
            reply_markup=reply_markup,
            parse_mode="markdown",
        )
    except Exception as e:
        LOGGER.error(str(e))


async def send_message(
    update, context, text: str, parse_mode="markdown", reply_to_message: bool = False
):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    args = {
        "chat_id": update.message.chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
        "allow_sending_without_reply": True,
        "disable_notification": True,
    }

    if reply_to_message:
        args["reply_to_message_id"] = update.message.message_id

    try:
        return await context.bot.send_message(**args)
    except Exception as e:
        LOGGER.error(str(e))


async def send_file(
    update,
    context: ContextTypes.DEFAULT_TYPE,
    file_path,
    chat_id: int | str | None = None,
    reply_to_message_id: int | None = None,
    caption: str | None = None,
):
    if not chat_id:
        chat_id = update.effective_chat.id

    await context.bot.send_chat_action(
        chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT
    )
    if isinstance(file_path, str):
        return await context.bot.send_document(
                    chat_id=chat_id,
                    document=file_path,
                    reply_to_message_id=reply_to_message_id,
                    caption=caption,
                )

    try:
        with open(file_path, "rb") as f:
            input_file = InputFile(f)
            return await context.bot.send_document(
                chat_id=chat_id,
                document=input_file,
                filename=f.name,
                reply_to_message_id=reply_to_message_id,
            )
    except Exception as e:
        LOGGER.error(f"Error al enviar documento: {str(e)}")

async def send_photo(update, context, file_path, text: str = "", reply_to_message=False, parse_mode="markdown", reply_markup=None, chat_id=None):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
    args = {
        "chat_id": chat_id or update.effective_chat.id,
        "caption": text,
        "parse_mode": parse_mode,
        "allow_sending_without_reply": True,
        "reply_markup": reply_markup,
    }
    if reply_to_message:
        args["reply_to_message_id"] = update.message.message_id
    try:
        with open(file_path, "rb") as f:
            input_file = InputFile(f)
            args["photo"] = input_file
            return await context.bot.send_photo(**args)
    except TelegramError as e:
        LOGGER.error(f"Error al enviar foto: {str(e)}")

async def send_markup(update, context, file_path, text: str, reply_markup: InlineKeyboardMarkup):
    return await send_photo(update, context, file_path, text, True, "markdown", reply_markup)

# def send_photo(
#     file_path,
#     update: Update,
#     text: str = "",
#     # chat_id: Union[int, str] = 0,
#     reply_to_message=False,
#     parse_mode="HTML",
#     reply_markup=None,
# ):
#     # update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)

#     # if chat_id:
#     #     ID_CHAT_POSTS = chat_id

#     args = {
#         "chat_id": ID_CHAT_POSTS,
#         "caption": text,
#         "parse_mode": parse_mode,
#         "allow_sending_without_reply": True,
#         "reply_markup": reply_markup,
#     }
#     if reply_to_message:
#         args["reply_to_message_id"] = update.message.message_id
#     try:
#         with open(file_path, "rb") as f:
#             input_file = InputFile(f)
#             args["photo"] = input_file
#             return upd_dis.bot.send_photo(**args)
#     except TelegramError as e:
#         LOGGER.error(f"Error al enviar foto: {str(e)}")


# # def edit_message


# def sendMarkup(
#     file_path, text: str, update: Update, reply_markup: InlineKeyboardMarkup
# ):
#     # return upd_dis.bot.send_message(update.message.chat_id,
#     #                         reply_to_message_id=update.message.message_id,
#     #                         text=text,
#     #                         reply_markup=reply_markup,
#     #                         allow_sending_without_reply=True,

#     #                         parse_mode='HTMl')
#     return send_photo(file_path, update, text, True, "HTML", reply_markup)


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
