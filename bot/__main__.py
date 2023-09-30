import codecs
import json
import math
# import os
import unicodedata
from typing import List, Optional


# import telegram
import requests
from bot import *
from bot.modules.the_movie_db import TheMovieDB
from bot.helpers.telegram_helper.decorators import is_authorised, is_owner
# from telegram.ext.utils.promise import CallbackContext
from bot.helpers.telegram_helper.msg_utils import delete_message, edit_message, send_file, send_message, send_photo
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

def parse_date(date_string: str) -> str:
    """
    Parses a date string in the format "dd mmm yyyy" and returns it in the format "yyyy-mm-dd".

    Args:
        date_string (str): The date string to be parsed.

    Returns:
        str: The parsed date string in the format "yyyy-mm-dd".
    """
    from datetime import datetime
    
    date_object = datetime.strptime(date_string, "%d %b %Y")
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date

def scrap_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

    _infoScrap = {}
    soup = BeautifulSoup(response.content, "html.parser")

    uploader = soup.find('h1').next.next
    title = soup.find('h1').find_all(text=True, recursive=False)[0].strip()

    info_movie = soup.find('div', {'class' : 'info_movie'}).find_all("p")

    _infoScrap["titulo"] = title
    _infoScrap["uploader"] = uploader
    _infoScrap["original_title"] = info_movie[1].find('a').text
    LOGGER.info(f"Se encontro el original_title {_infoScrap['original_title']}")

    _infoScrap["ano"] = info_movie[3].find('a').text
    # print(info_movie[4].find('span').text)
    _infoScrap["release_date"] = parse_date(info_movie[4].find('span').text.strip())
    # print(parse_date(info_movie[4].find('span').text.strip()))

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

def create_file(file_path : str, data : str = None):
    # with codecs.open(file_path, "a", "utf-8") as archivo:
    #     archivo.write(data_movie)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def read_file(folder_path : str, file_path : str) -> dict:
    with open(f"{folder_path}/{file_path}.json", 'r', encoding='utf-8') as json_file:
        return json.load(json_file)

def delete_file(file_path : str):
    os.remove(file_path)

def make_folder(folder_path : str):
    os.makedirs(folder_path, exist_ok=True)  # Crea la carpeta si no existe

def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = send_message("Starting Ping", update)
    end_time = int(round(time.time() * 1000))
    edit_message(f'{end_time - start_time} ms', reply)

# TODO: Revisar y havcer que envie los logs segun la fecha
def send_log(update, context):
    send_file('log.txt', update)

def download_url(url: str):
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

def posst(media_type, file_path, update, context):
    data = read_file(media_type, file_path)

    image = download_url(f"{URL_IMAGE}{data['poster_path']}")
    send_photo(image, update)

    msg = f"<b>{(data.get('title') or data.get('name'))} ({(data.get('release_date') or data.get('first_air_date'))[:4]})</b>"
    msg = f"{msg}\n<i>{data['tagline']}</i>\n"
    msg = f"{msg}\n<b>Sinopsis</b>:\n{data['overview']}\n\n"
    if data.get('runtime'):
        msg = f"{msg}\n{data['runtime']} min\n"
    if data.get('number_of_episodes'):
        msg = f'{msg}\nTemporadas: {data["number_of_seasons"]} Episodios: {data["number_of_episodes"]}\n'
    for gener in data['genres']:
        if "-" in gener["name"]:
            gener["name"] = gener["name"].replace("-", "_")

        if "&" in gener["name"]:
            sub_genes = gener["name"].split("&")
            for sub_gene in sub_genes:
                msg = f"{msg}#{sub_gene.strip()} "
        else:
            msg = f"{msg}#{gener['name']} "

    msg = f"{msg}\n<a href='https://www.imdb.com/title/{data['external_ids']['imdb_id']}/'>IMDB</a> - <a href='https://www.themoviedb.org/{media_type}/{data['id']}?language=es'>TMDB</a>"

    send_message(msg, update)
    
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


def get_link(update):
    args = update.message.text.split(' ')

    try:
        link = args[1]
        LOGGER.info("Se obtuvo correctamente el enlace!")
    except IndexError:
        link = ''
        LOGGER.info("No se obtuvo el enlace!")

    if link != '':
        LOGGER.info(link)
    link = link.strip()
    reply_to = update.message.reply_to_message

    if reply_to is not None:
        LOGGER.info("Se esta intentando obtener el enlace de un mensaje de respuesta!")
        file = None
        media_array = [reply_to.document, reply_to.video, reply_to.audio, 
                    #    reply_to.photo #alparecer siempre esta en el mensaje de respuesta
                       ]
        
        for item in media_array:
            if item is not None:
                file = item
                LOGGER.info("Se encontro que hay un tipo de archivo en la respuesta!")
                break
                
        if file is None:
            LOGGER.info("Se encontro que no hay un tipo de archivo en la respuesta!")
            if reply_to.text is not None:
                reply_text = reply_to.text
                if is_valid_link(reply_text) or is_themoviedb_url(reply_text):
                    link = reply_text
                    LOGGER.info("Se encontro un enlace en el texto!")
                    
        if reply_to.caption is not None:
            reply_text = reply_to.caption_entities[2]['url']
            if is_themoviedb_url(reply_text):
                link = reply_text
                LOGGER.info("Se encontro un enlace en el caption!")
                
    return link


def post_info(update, context):
    link = get_link(update)
    
    try:
        media_type, file_path = link.split("/")[-2:]
        LOGGER.info("Se obtuvo correctamente el tipo de media y el directorio del archivo!")
        
        posst(media_type, file_path, update, context) 
        
    except IndexError:
        print('Ocurrió un error de índice al dividir el enlace')
    except Exception as e:
        print('Ocurrió una excepción:', e)



def load_data(update, is_movie):
    link = get_link(update)

    media_type = 'movie' if is_movie else 'tv'

    if is_valid_link(link):
        msg = send_message(f"<b>Scrapeando:</b> <code>{link}</code>", update)
        data_scrap = scrap_url(link)
        tmdb = TheMovieDB(data_scrap["original_title"], data_scrap["release_date"])
        data_media = tmdb.search_movies() if is_movie else tmdb.search_tv_shows()

        if data_media:
            file_name = download_url(data_scrap['imagen'])
            text = f'<b>{data_scrap["original_title"]}</b>\n<i>{data_scrap["titulo"]}</i>\n<a href="https://www.themoviedb.org/{media_type}/{data_media["id"]}">themoviedb</a>'
            send_photo(file_name, update, text)
            create_file(f'{media_type}/{data_media["id"]}.json', data_media)
            delete_file(file_name)


            # create_file(f'tv/{data_movie["id"]}.json', data_movie)
        # # create_file(f'{file_name}.txt')
        # # send_file(f'{file_name}.txt',  update)
        # # delete_file(f'{file_name}.txt')
        else:
            print("No se encontraron resultados.")
            return None
        
        delete_message(msg)

    else:
        send_message("Proporciona un enlace valido", update)


@is_authorised
def post_movie(update, context):
    load_data(update, True)

@is_authorised
def post_tv(update, context):
    load_data(update, False)

# @run_async
def start(update, context):
    send_message("waked up😏😏😏", update)

def main():
    start_handler = CommandHandler("start", start, pass_args=True, run_async=True)
    post_movie_handler = CommandHandler('movie', post_movie)
    post_tv_handler = CommandHandler('show', post_tv)
    post_info_handler = CommandHandler('info', post_info)
    ping_handler = CommandHandler('ping', ping)
    send_log_handler = CommandHandler('log', send_log)
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
    make_folder('tv')
    make_folder('movie')
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
    # data_scrap = scrap_url('https://www.latinomegahd.net/futurama-serie-de-tv-temporada-10-2013-latino-hd-dsnp-web-dl-1080p/')
    # print(scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/'))
    # data_scrap = scrap_url('https://www.latinomegahd.net/amenaza-bajo-el-agua-no-podras-escapar-2020-latino-hd-brrip-1080p/')
    # data_scrap = scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/')
    # tmdb = TheMovieDB(data_scrap["original_title"], data_scrap["release_date"])
    # tmdb.search_tv_shows()
    # tmdb.search_movies()
    # create_file(f'movie/884605.json')

# TODO: crera carprta data para allmacenar las igs