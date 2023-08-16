import codecs
import json
import math
# import os
import unicodedata
from typing import List, Optional

# import telegram
import requests
from bot import *
from bot.decorators import is_authorised, is_owner
# from telegram.ext.utils.promise import CallbackContext
from bot.msg_utils import deleteMessage, editMessage, sendFile, sendMessage, sendPhoto
from bs4 import BeautifulSoup
# from telegram import Message, Chat, Update, Bot, User
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
# from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler
from tqdm import tqdm

# from telegram.ext.dispatcher import run_async, DispatcherHandlerStop
# from telegram.utils.helpers import escape_markdown

# from telegram.message import Message
# from telegram.update import Update

# from telegram.ext import Updater
# from telegram import InputFile


data_movie = {}
class TheMovieDB:
    def __init__(self, title: str, release_date: str) -> None:
        self.title = title
        self.release_date = release_date
        self.ID: int = None

    def _get_search_results(self, search_name=None, search_id=None) -> dict:
        payload = {}
        headers = {'Authorization': ACCESS_TOKEN_AUTH}
        _url = f"{URL_THEMOVIEDB}{search_name or search_id}"

        if not search_name:
            _url = f"{_url}{self.ID}?append_to_response=external_ids"

        if not search_id:
            _url = f"{_url}?query={self.title.replace(' ', '+')}&include_adult=true"
            # "&primary_release_year=2006&page=1"
        _url = f"{_url}&language={LANGUAGE}"

        try:
            response = requests.get(_url, headers=headers, data=payload)
            response.raise_for_status()  # Manejo de errores HTTP
            # print(response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en la solicitud: {e}")  # Elevación de excepción

    def search_movies(self):
        # global data_movie
        response = self._get_search_results(SEARCH_NAME_MOVIE)

        if not (response and response["total_results"] != 0):
            print("No es una película o está escrita de manera incorrecta")
            return None

        for result in response["results"]:
            if (
                result["original_title"] == self.title
                and (
                    self.release_date == result["release_date"]
                    or self.release_date[:4] == result["release_date"][:4]
                )
            ):
                self.ID = result["id"]
                break

        if self.ID:
            return self._get_search_results(None, SEARCH_ID_MOVIE)
        return None

    def search_tv_shows(self):
        # global data_movie
        response = self._get_search_results(SEARCH_NAME_TV)

        if not (response and response["total_results"] != 0):
            print("No es una serie o está escrita de manera incorrecta")
            return None

        for result in response["results"]:
            if (
                result["original_name"] == self.title
                and self.release_date == result["first_air_date"]
            ):
                self.ID = result["id"]
                break

        if self.ID:
            return self._get_search_results(None, SEARCH_ID_TV)
        return None


        # print(data_movie)
        # return
#         # else:
#         #     print("No se encotro la serie")

def _parse_date(date : str) -> str:
    from datetime import datetime

    fecha_objeto = datetime.strptime(date, "%d %b %Y")
    fecha_convertida = fecha_objeto.strftime("%Y-%m-%d")
    return fecha_convertida

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
    _infoScrap["original_title"] = info_movie[1].find('a').text
    _infoScrap["ano"] = info_movie[3].find('a').text
    # print(info_movie[4].find('span').text)
    _infoScrap["release_date"] = _parse_date(info_movie[4].find('span').text.strip())

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
def create_file(file_path : str, data : str = None):
    # with codecs.open(file_path, "a", "utf-8") as archivo:
    #     archivo.write(data_movie)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def read_file(folder_path, file_path):
    with open(f"{folder_path}/{file_path}.json", 'r', encoding='utf-8') as json_file:
        return json.load(json_file)

def delete_file(file_path : str):
    os.remove(file_path)

def make_folder(folder_path : str):
    os.makedirs(folder_path, exist_ok=True)  # Crea la carpeta si no existe

def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)

def sendlog(update, context):
    sendFile('log.txt', context.bot, update)

def downloadUrl(url: str):
    file_name = url.split("/")[-1].replace("%2B", " ")

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
        # print("Descarga completada.")
        LOGGER.info(f"{file_name} > Descarga completada.")
        return file_name
    
def is_valid_link(url: str):
    return HOST in url

def is_themoviedb_url(url: str):
    return "themoviedb.org" in url

def posst(folder_path, file_path, update, context):
    data = read_file(folder_path, file_path)

    image = downloadUrl(f"{URL_IMAGE}{data['poster_path']}")
    sendPhoto(image, update)

    msg = f"<b>{(data.get('title') or data.get('name'))} ({(data.get('release_date') or data.get('first_air_date'))[:4]})</b>"
    msg = f"{msg}\n<i>{data['tagline']}</i>\n"
    msg = f"{msg}\n<b>Sinopsis</b>:\n{data['overview']}\n\n"
    if data.get('runtime'):
        msg = f"{msg}\n{data['runtime']} min\n"
    for genre in data['genres']:
        msg = f"{msg}#{genre['name']} "
    if data.get('number_of_episodes'):
        msg = f'{msg}\nTemporadas: {data["number_of_seasons"]} Episodios: {data["number_of_episodes"]}'

    msg = f"{msg}\n<a href='https://www.themoviedb.org/movie/{data['id']}?language=es'>TMDB</a> - <a href='https://www.imdb.com/title/{data['external_ids']['imdb_id']}/'>IMDB</a>"
    sendMessage(msg, context.bot, update)

    

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

    # print(msg)

def post_info(update, context):
    args = update.message.text.split(' ')
    
    try:
        link = args[1]
    except IndexError:
        link = ''
    
    if link != '':
        LOGGER.info(link)
    link = link.strip()
    reply_to = update.message.reply_to_message

    if reply_to is not None:
        file = None
        media_array = [reply_to.document, reply_to.video, reply_to.audio, reply_to.photo]
        for i in media_array:
            if i is not None:
                file = i
                break
        if file is None:
            if reply_to.text is not None:
                reply_text = reply_to.text
                if is_themoviedb_url(reply_text):
                    link = reply_text
        if reply_to.caption is not None:
            reply_text = reply_to.caption_entities[2]['url']
            if is_themoviedb_url(reply_text):
                link = reply_text
    # print(link)
    # return
    folder_path, file_path = link.split("/")[-2:]
    posst(folder_path, file_path, update, context)


def get_link(update):
    args = update.message.text.split(' ')
    
    try:
        link = args[1]
    except IndexError:
        link = ''
    
    if link != '':
        LOGGER.info(link)
    link = link.strip()
    reply_to = update.message.reply_to_message

    if reply_to is not None:
        file = None
        media_array = [reply_to.document, reply_to.video, reply_to.audio, reply_to.photo]
        for i in media_array:
            if i is not None:
                file = i
                break
        if file is None:
            reply_text = reply_to.text
            if is_valid_link(reply_text):
                link = reply_text
    return link

@is_authorised
def post_movie_Node(update, context):
    link = get_link(update)

    if is_valid_link(link):
        msg = sendMessage(f"<b>Scrapeando:</b> <code>{link}</code>", context.bot, update)
        info_scrap = scrap_url(link)
        # print('info_scrap')
        tmdb = TheMovieDB(info_scrap["original_title"], info_scrap["release_date"])
        data_movie = tmdb.search_movies()

        if not data_movie:
            print("No se encontraron resultados.")
            return None

        # info_movie = movies(info_scrap)
        file_name = downloadUrl(info_scrap['imagen'])

        sendPhoto(file_name, update, context.bot, f'<b>{info_scrap["original_title"]}</b>\n<i>{info_scrap["titulo"]}</i>\n<a href="https://www.themoviedb.org/movie/{data_movie["id"]}">themoviedb</a>')
        make_folder('movie')
        create_file(f'movie/{data_movie["id"]}.json', data_movie)

        # # create_file(f'{file_name}.txt')
        # # sendFile(f'{file_name}.txt', context.bot, update)
        # # delete_file(f'{file_name}.txt')
        delete_file(file_name)


    else:
        sendMessage("Proporciona un enlace valido", context.bot, update)

@is_authorised
def post_tv_Node(update, context):
    link = get_link(update)

    if is_valid_link(link):
        msg = sendMessage(f"<b>Scrapeando:</b> <code>{link}</code>", context.bot, update)
        info_scrap = scrap_url(link)
        # print('info_scrap')
        tmdb = TheMovieDB(info_scrap["original_title"], info_scrap["release_date"])
        data_movie = tmdb.search_tv_shows()

        if data_movie:
            print(data_movie)
        else:
            print("No se encontraron resultados.")
            return None

        # info_movie = movies(info_scrap)
        file_name = downloadUrl(info_scrap['imagen'])

        sendPhoto(file_name, update, context.bot, f'<b>{info_scrap["original_title"]}</b>\n<i>{info_scrap["titulo"]}</i>\n<a href="https://www.themoviedb.org/tv/{data_movie["id"]}">themoviedb</a>')
        make_folder('tv')
        create_file(f'tv/{data_movie["id"]}.json', data_movie)

        # sendFile(f'{file_name}.txt', context.bot, update)
        # delete_file(f'{file_name}.txt')
        delete_file(file_name)


    else:
        sendMessage("Proporciona un enlace valido", context.bot, update)

# @run_async
def start(update, context):
    sendMessage("waked up😏😏😏", context.bot, update)

def main():
    start_handler = CommandHandler("start", start, pass_args=True, run_async=True)
    post_movie_handler = CommandHandler('movie', post_movie_Node)
    post_tv_handler = CommandHandler('show', post_tv_Node)
    post_info_handler = CommandHandler('info', post_info)
    ping_handler = CommandHandler('ping', ping)
    send_log_handler = CommandHandler('log', sendlog)
    # start_handler = CommandHandler("start", start, pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(post_movie_handler)
    dispatcher.add_handler(post_tv_handler)
    dispatcher.add_handler(post_info_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(send_log_handler)
#
    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4)
    LOGGER.info("Bot Started!")

    updater.idle()



if __name__ == '__main__':
    # LOGGER.info("Successfully loaded modules: ")
    main()
    # print(read_file('movie', '884605'))
    # posst()

    # read_file('tv', '615')
    # tmdb = TheMovieDB("Cars", "2006-06-08")
    # tmdb.search_movies()
    # print(tmdb.search_movies())
    # tmdb = TheMovieDB("Sex Education", "2019-01-11")
    # print(tmdb.search_tv_shows())
    # create_file('movies/test.txt')
    # info_scrap = scrap_url('https://www.latinomegahd.net/futurama-serie-de-tv-temporada-10-2013-latino-hd-dsnp-web-dl-1080p/')
    # print(scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/'))
    # info_scrap = scrap_url('https://www.latinomegahd.net/amenaza-bajo-el-agua-no-podras-escapar-2020-latino-hd-brrip-1080p/')
    # info_scrap = scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/')
    # tmdb = TheMovieDB(info_scrap["original_title"], info_scrap["release_date"])
    # tmdb.search_tv_shows()
    # tmdb.search_movies()
    # create_file(f'movie/884605.json')

