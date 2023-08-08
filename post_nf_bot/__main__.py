# import importlib
import re
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from telegram.ext.dispatcher import run_async, DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown

# from telegram.message import Message
# from telegram.update import Update

# from telegram.ext.utils.promise import CallbackContext

from post_nf_bot import *

import os
# import json
import math
import codecs
import telegram
import requests
import unicodedata
from tqdm import tqdm
from bs4 import BeautifulSoup
# from telegram.ext import Updater
from telegram import InputFile

# from importlib.resources import contents
# from urllib import response
# import requests
import json
# import CrearHtml


info_movie = {}

def movies(data):
    SEARCH_NAME = SEARCH_NAME_MOVIE
    SEARCH_ID = SEARCH_ID_MOVIE

    titulo = data["titleOriginal"]
    titulo = titulo.replace(' ', '+')
    
    request = requests.get(f"{URL}{SEARCH_NAME}?api_key={API}&query={titulo}")
    response = json.loads(request.text)
    
    if (response["total_results"] != 0):
        
        for resultados in response["results"]:
            if(resultados["title"] == data["titleOriginal"] and data["ano"] in resultados["release_date"]):
                ide = resultados["id"]

        request = requests.get(f"{URL}{SEARCH_ID}{ide}?api_key={API}&language={LANGUAGE}")
        response = json.loads(request.text)
        return response

    else:
        print("No es una pelicula o esta escrita de manera incorrecta")

# 
def scrap_url(url):
    _infoScrap = {}

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

    soup = BeautifulSoup(response.content, "html.parser")
    
    uploader = soup.find('h1').next.next
    title = soup.find('h1').find_all(text=True, recursive=False)[0].strip()

    info_movie = soup.find('div', {'class' : 'info_movie'}).find_all("p")
    # print(title, type(title))
    # exit()


    _infoScrap["titulo"] = title
    _infoScrap["uploader"] = uploader
    _infoScrap["titleOriginal"] = info_movie[1].find('a').text
    _infoScrap["ano"] = info_movie[3].find('a').text

    contenido = soup.find('div', {'class' : 'post-content'})
    
    img_scrap = contenido.find('img', {'class' : 'alignnone size-medium'}, src=True)
    if not img_scrap:
    # else:
        img_scrap = contenido.find('img', {'class' : 'alignnone'}, src=True)
    _infoScrap["imagen"] = img_scrap['src']

    _infoScrap["title"] = contenido.find("h5").next.next
    
    allP = contenido.find_all("p", limit=5)
    
    _infoScrap["sipnosis"] = allP[2].text
    
    datosTecnicos = unicodedata.normalize("NFKD", allP[4].text) #Delete '\xa0' from string

    _infoScrap["datosTecnicos"] = datosTecnicos


    return _infoScrap

# 


def send_file(file_path):
    # Abrir el archivo
    with open(file_path, 'rb') as f:
        input_file = InputFile(f)
        # Enviar archivo al chat
    try:
        updater.bot.send_document(chat_id=ID_CHAT, document=input_file)
    except telegram.error.TelegramError as e:
        print(f"Error al enviar documento: {e}")

def deleteFile(fileName):
    os.remove(fileName)

def writeFile(fileName):
    archivo = codecs.open(fileName, "a", "utf-8")
    archivo.write(f'{info_movie}')

def send_img(file_path, bot, text=''):
    # print(info_movie)
    # exit()
    # Abrir el archivo
    with open(file_path, 'rb') as f:
        input_file = InputFile(f)
        # Enviar archivo al chat
        # updater.bot.send_document(chat_id='-1001596325178', document=input_file)
    try:
        bot.send_photo(chat_id=ID_CHAT_POSTS, photo=input_file, caption=text, parse_mode=ParseMode.HTML)
        # updater.bot.send_document(chat_id=ID, document=input_file)
    except telegram.error.TelegramError as e:
        print(f"Error al enviar documento: {e}")

def downloadUrl(url: str):
    file_name = url.split("/")[-1].replace("%2B", " ")
    print(file_name, "ok")

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    written = 0

    with open(file_name, "wb") as f:
        for data in tqdm(response.iter_content(block_size), total=math.ceil(total_size//block_size), unit='KB', unit_scale=True):
            written = written + len(data)
            f.write(data)

    if total_size != 0 and written != total_size:
        print("Error durante la descarga.")
    else:
        print("Descarga completada.")
        return file_name


def sendMessage(text: str, bot, update: Update, parse_mode='HTMl'):
    return bot.send_message(update.message.chat_id,
                            reply_to_message_id=update.message.message_id,
                            text=text,
                            parse_mode=parse_mode)

def postNode(update, context):
    args = update.message.text.split(" ")
    if len(args) > 1:
        link = args[1]

        if HOST in link:
            msg = sendMessage(f"<b>Scrapeando:</b> <code>{link}</code>", context.bot, update)
            info_scrap = scrap_url(link)
            print('info_scrap')
            info_movie = movies(info_scrap)
            print('info_movie')
            file_name = downloadUrl(info_scrap['imagen'])
            send_img(file_name, context.bot, f'<b>{info_scrap["titleOriginal"]}</b>\n<i>{info_scrap["titulo"]}</i>')
            # writeFile(f'{file_name}.txt')
            # send_file(f'{file_name}.txt')
            # deleteFile(f'{file_name}.txt')
            deleteFile(file_name)

            
        else:
            sendMessage("Proporciona un enlace valido", context.bot, update)
    else:
        sendMessage("Por favor proporciona un enlace.", context.bot, update)

# @run_async
def start(update, context):
    context.bot.send_message(update.message.chat_id,
                     reply_to_message_id=update.message.message_id,
                            text="waked up😏😏😏")

def main():

    LOGGER.info("Bot Started!")

    start_handler = CommandHandler("start", start, pass_args=True, run_async=True)
    post_handler = CommandHandler('post', postNode)
    # start_handler = CommandHandler("start", start, pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(post_handler)

# 
    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4)

    updater.idle()



if __name__ == '__main__':
    # LOGGER.info("Bot Started!")
    # LOGGER.info("Successfully loaded modules: ")
    main()
