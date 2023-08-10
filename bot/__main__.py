from typing import Optional, List

# from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import CommandHandler, Filters, MessageHandler, CallbackQueryHandler
# from telegram.ext.dispatcher import run_async, DispatcherHandlerStop
# from telegram.utils.helpers import escape_markdown

# from telegram.message import Message
# from telegram.update import Update

# from telegram.ext.utils.promise import CallbackContext
from bot.msg_utils import deleteMessage, sendMessage, sendFile, sendPhoto
from bot.decorators import is_authorised, is_owner
from bot import *

import os
import json
import math
import codecs
# import telegram
import requests
import unicodedata
from tqdm import tqdm
from bs4 import BeautifulSoup
# from telegram.ext import Updater
# from telegram import InputFile


data_movie = {}

class themoviedb:
    def __init__(self, title:str, ano:str) -> None:
        # pass
        self.title = title
        self.ano = ano
        self.ID : int = None
        self.API = '12c73c03e322d7711c1bf808d29b35be'
        self.LANGUAGE = 'es-MX'
        self.URL = 'https://api.themoviedb.org/3/'

        self.SEARCH_NAME_MOVIE = 'search/movie'
        self.SEARCH_NAME_TV = 'search/tv'
        self.SEARCH_ID_MOVIE = 'movie/'
        self.SEARCH_ID_TV = 'tv/'
    
    def _get_search_results(self, search_name=None, search_id=None):
        request = requests.get(f"{self.URL}{search_name or search_id}?api_key={self.API}&query={self.title.replace(' ', '+')}")
        response = json.loads(request.text)
        return response
    
    def search_tv_shows(self):
        response = self._get_search_results(self.SEARCH_NAME_TV)

        if (response["total_results"] != 0):
            for resultados in response["results"]:
                if(resultados["name"] == self.title):
                    self.ID = resultados["id"]
            

            
#             ide = str(ide)
#             request = requests.get(f"{URL}{SEARCH_ID}{ide}?api_key={API}&language={LANGUAGE}")
#             response = json.loads(request.text)

#             if(len(response.keys()) != 2):
#                 titulo = response["name"]
#                 generos = ""
#                 for gen in response["genres"]:
#                     generos += gen["name"] + ", "
#                 generos = generos[:len(generos) -2]
#                 # sipnosis = response["overview"]
#                 # imdbID = response["imdb_id"]
#                 temporadas = response["seasons"]
#                 if response["status"] == "Canceled":
#                     estado = "Cancelada"
#                 else:
#                     estado = "En produccion"
                
#                 for temporada in temporadas:
#                     seasonId = temporada["id"]
#                     seasonDate = temporada["air_date"]
#                     seasonEpisodes = temporada["episode_count"]
#                     seasonName = temporada["name"]
#                     # seasonOverview = temporada["overview"]
#                     seasonPoster = temporada["poster_path"]

#                     print(seasonId,seasonDate,seasonEpisodes,seasonName,seasonPoster)



#         # else:
#         #     print("No se encotro la serie")
#     else:
#         print("No es una serie o esta escrita de manera incorrecta")
    
    def search_movies(self):
        global data_movie
        response = self._get_search_results(self.SEARCH_NAME_MOVIE)
        
        if (response["total_results"] != 0):
            for resultados in response["results"]:
                if(resultados["title"] == self.title and self.ano in resultados["release_date"]):
                    self.ID = resultados["id"]
                    break
                else:
                    self.ID = None
            
            request = requests.get(f"{self.URL}{self.SEARCH_ID_MOVIE}{self.ID}?api_key={self.API}&language={self.LANGUAGE}")
            response = json.loads(request.text)
            # return response
            data_movie = response
        else:
            data_movie = {}
            print("No es una pelicula o esta escrita de manera incorrecta")

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

def deleteFile(fileName):
    os.remove(fileName)

def writeFile(fileName):
    with codecs.open(fileName, "a", "utf-8") as archivo:
        archivo.write(f'{data_movie}') #corregir la variable


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

@is_authorised
def postNode(update, context):
    args = update.message.text.split(" ")
    if len(args) > 1:
        link = args[1]

        if HOST in link:
            msg = sendMessage(f"<b>Scrapeando:</b> <code>{link}</code>", context.bot, update)
            info_scrap = scrap_url(link)
            print('info_scrap')

            bot = themoviedb(info_scrap["titleOriginal"], info_scrap["ano"])
            bot.search_movies()

            # info_movie = movies(info_scrap)
            print('data_movie')
            # print(data_movie)
            file_name = downloadUrl(info_scrap['imagen'])

            sendPhoto(file_name, context.bot, f'<b>{info_scrap["titleOriginal"]}</b>\n<i>{info_scrap["titulo"]}</i>\n<a href="https://www.themoviedb.org/movie/{data_movie["id"]}">themoviedb</a> - <a href="https://www.imdb.com/title/{data_movie["imdb_id"]}/">imdb</a>')
            # # writeFile(f'{file_name}.txt')
            # # sendFile(f'{file_name}.txt', context.bot, update)
            # # deleteFile(f'{file_name}.txt')
            deleteFile(file_name)


        else:
            sendMessage("Proporciona un enlace valido", context.bot, update)
    else:
        sendMessage("Por favor proporciona un enlace.", context.bot, update)

@is_authorised
def post_tv_show_Node(update, context):
    args = update.message.text.split(" ")
    if len(args) > 1:
        link = args[1]

        if HOST in link:
            msg = sendMessage(f"<b>Scrapeando:</b> <code>{link}</code>", context.bot, update)
            info_scrap = scrap_url(link)
            print('info_scrap')
            bot = themoviedb(info_scrap["titleOriginal"], info_scrap["ano"])
            bot.search_movies()

            # info_movie = movies(info_scrap)
            file_name = downloadUrl(info_scrap['imagen'])

            sendPhoto(file_name, context.bot, f'<b>{info_scrap["titleOriginal"]}</b>\n<i>{info_scrap["titulo"]}</i>\n<a href="https://www.themoviedb.org/movie/{data_movie["id"]}">themoviedb</a> - <a href="https://www.imdb.com/title/{data_movie["imdb_id"]}/">imdb</a>')
            # writeFile(f'{file_name}.txt')
            # sendFile(f'{file_name}.txt', context.bot, update)
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
    post_handler = CommandHandler('movie', postNode)
    post_tv_show_handler = CommandHandler('show', post_tv_show_Node)
    # start_handler = CommandHandler("start", start, pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(post_handler)
    dispatcher.add_handler(post_tv_show_handler)

# 
    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4)

    updater.idle()


if __name__ == '__main__':
    # LOGGER.info("Successfully loaded modules: ")
    main()
    