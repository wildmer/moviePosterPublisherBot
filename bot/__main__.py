# import codecs
import json
import math
# import os
# import unicodedata
# from typing import List, Optional
from pathlib import Path
from time import sleep, time

# import telegram
import requests  # type:ignore
from bs4 import BeautifulSoup  # type:ignore
from telegram import (  # ReplyKeyboardMarkup,; ReplyKeyboardRemove,; Update,; InlineKeyboardButton,; ParseMode
    InlineKeyboardMarkup, InputMediaPhoto)
from telegram.ext import (  # Application,; ContextTypes,; ConversationHandler,; MessageHandler,; filters,
    CallbackQueryHandler, CommandHandler)
from tqdm import tqdm  # type:ignore

# from bot import *
from bot import LOGGER, upd_dis, updater
from bot.config import HOST, NO_IMAGE, URL_IMAGE
from bot.helpers.helper_funcs.filters import CustomFilters
# from telegram.ext.utils.promise import CallbackContext
from bot.helpers.telegram_helper.button_build import ButtonMaker
from bot.helpers.telegram_helper.decorators import is_authorised
from bot.helpers.telegram_helper.msg_utils import (delete_message,
                                                   edit_message, send_file,
                                                   send_message, send_photo,
                                                   sendMarkup)
from bot.modules.the_movie_db import TheMovieDB

# from telegram import Message, Chat, Update, Bot, User

# from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError




tmdb = None

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


def scrap_url(url) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

    # Obtener la codificación de la respuesta
    encoding = response.encoding

    # _infoScrap = {}
    soup = BeautifulSoup(response.content, "html.parser", from_encoding=encoding)

    ts = soup.find("div", {"class": "post-ratings"})
    post_id = ts["data-nonce"]

    url = f"https://www.latinomegahd.net/wp-json/wp/v2/posts/{post_id}"
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

    # save the response as a json file
    data = json.loads(response.text[1:])  # el primer caracter generar un error

    return data
    # uploader = soup.find("h1").find("i").text
    # title = soup.find("h1").find_all(text=True, recursive=False)[0]

    # info_movie = soup.find("div", {"class": "info_movie"}).find_all("p")  # type:ignore

    # _infoScrap["titulo"] = title
    # _infoScrap["uploader"] = uploader
    # tl = info_movie[1].find("a") or info_movie[1].find("span")
    # _infoScrap["original_title"] = tl.text
    # LOGGER.info(f"Se encontro el original_title {_infoScrap['original_title']}")

    # duration = info_movie[2].find("a") or info_movie[2].find("span")
    # i = 0
    # if not ("min" in duration.text or "N/A" in duration.text):
    #     LOGGER.info("Se restara 1")
    #     i = 1

    # date_movie = info_movie[3 - i].find("a") or info_movie[3 - i].find("span")
    # _infoScrap["ano"] = date_movie.text

    # date_get = info_movie[4 - i].find("span")
    # if "N/A" in duration.text:
    #     date_get = ""
    # else:
    #     date_get = parse_date(date_get.text.strip())

    # _infoScrap["release_date"] = date_get
    # # print(parse_date(info_movie[4].find('span').text.strip()))

    # contenido = soup.find("div", {"class": "post-content"})

    # img_scrap = contenido.find("img", {"class": "alignnone size-medium"}, src=True)  # type:ignore
    # if not img_scrap:
    #     # else:
    #     img_scrap = contenido.find("img", {"class": "alignnone"}, src=True)  # type:ignore
    # _infoScrap["imagen"] = img_scrap["src"]  # type:ignore

    # _infoScrap["title"] = contenido.find("h5").next.next  # type:ignore

    # allP = contenido.find_all("p", limit=5)  # type:ignore

    # _infoScrap["sipnosis"] = allP[2].text

    # datosTecnicos = unicodedata.normalize(
    #     "NFKD", allP[4].text
    # )  # Delete '\xa0' from string

    # _infoScrap["datosTecnicos"] = datosTecnicos

    # return _infoScrap


def create_file(file_path: str, data: str = ""):
    # with codecs.open(file_path, "a", "utf-8") as archivo:
    #     archivo.write(data_movie)
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def read_file(folder_path: str, file_path: str) -> dict:
    with open(f"{folder_path}/{file_path}.json", "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def delete_file(file_path: str) -> None:
    """
    Deletes a file at the specified file path.

    Args:
        file_path (str): The path of the file to be deleted.
    """
    Path(file_path).unlink()


def make_folder(folder_path: str) -> None:
    """
    Crea una carpeta en la ruta especificada.

    Args:
        folder_path (str): La ruta de la carpeta a crear.

    Returns:
        None
    """
    Path(folder_path).mkdir(parents=True, exist_ok=True)  # Crea la carpeta si no existe


def ping(update, context):
    """
    Function to measure the response time of the bot.

    Args:
        update: The update object containing information about the incoming message.
        context: The context object containing additional information.

    Returns:
        None
    """
    start_time = int(round(time() * 1000))
    reply = send_message("Starting Ping", update)
    end_time = int(round(time() * 1000))
    edit_message(f"{end_time - start_time} ms", reply)


# TODO: Revisar y havcer que envie los logs segun la fecha
def send_log(update, context):
    send_file("log.txt", update)


def download_url(url: str | None, is_poster: bool = True):
    if url is None:
        return NO_IMAGE
    if is_poster:
        url = URL_IMAGE + url
    file_name = url.split("/")[-1].replace("%2B", " ")

    if "i.imgur.com/" in url:
        LOGGER.info("Se encontro un enlace de imgur")
        url = "https://imgur.com/download/" + file_name.split(".")[0] + "/"
        LOGGER.info(f"Nuevo enlace: {url}")

    file = f"poster/{file_name}"

    if Path(file).exists():
        LOGGER.info(f"El archivo {file_name} ya existe.")
        return file

    response = requests.get(url, stream=True)
    status_code = response.status_code
    if status_code == 429:
        LOGGER.info("Se ha alcanzado el límite de solicitudes.")
        raise Exception("Se ha alcanzado el límite de solicitudes.")
        # return
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    written = 0

    with open(file, "wb") as f:
        for data in tqdm(
            response.iter_content(block_size),
            total=math.ceil(total_size // block_size),
            unit="KB",
            unit_scale=True,
        ):
            written = written + len(data)
            f.write(data)

    if total_size != 0 and written != total_size:
        print("Error durante la descarga.")
    else:
        # print("Descarga completada.")
        LOGGER.info(f"{file_name} > Descarga completada.")
        return file


def is_valid_link(url: str):
    return HOST in url


def is_themoviedb_url(url: str):
    return "themoviedb.org" in url


def posst(media_type: str, file_path: str, update, context):
    data = read_file(media_type, file_path)

    image = download_url(f"{data['poster_path']}")
    send_photo(image, update, reply_to_message=True)
    # send_photo(image, update, reply=True)

    title: str = str(data.get("title") or data.get("name"))
    date: str = data.get("release_date") or data.get("first_air_date", [])[:4]

    msg = f"<b>{title} ({date})</b>"
    msg = f"{msg}\n<i>{data['tagline']}</i>\n"
    msg = f"{msg}\n<b>Sinopsis</b>:\n{data['overview']}\n\n"
    if data.get("runtime"):
        msg = f"{msg}\n{data['runtime']} min\n"
    if data.get("number_of_episodes"):
        msg = f'{msg}\nTemporadas: {data["number_of_seasons"]} Episodios: {data["number_of_episodes"]}\n'
    for gener in data["genres"]:
        if "-" in gener["name"]:
            gener["name"] = gener["name"].replace("-", "_")
        
        if " " in gener["name"]:
            gener["name"] = gener["name"].replace(" ", "_")

        if "&" in gener["name"]:
            sub_genes = gener["name"].split("&")
            for sub_gene in sub_genes:
                msg = f"{msg}#{sub_gene.strip()} "
        else:
            msg = f"{msg}#{gener['name']} "

    msg = f"{msg}\n<a href='https://www.imdb.com/title/{data['external_ids']['imdb_id']}/'>IMDB</a> - <a href='https://www.themoviedb.org/{media_type}/{data['id']}?language=es'>TMDB</a>"

    send_message(msg, update, reply_to_message=True)

    if media_type == "tv":
        tmdb = TheMovieDB(title, date)
        tmdb.setId(data["id"])
        for season in data["seasons"]:
            if season["season_number"] == 0:
                continue
            LOGGER.info(f"Season: {season['season_number']}")
            season_image = download_url(f"{season['poster_path']}")
            data_season = tmdb.search_season_tv_shows(season["season_number"])
            sleep(4)
            file_name = f'tv/{data_season.get("_id", "temp")}.json'
            create_file(file_name, data_season)

            send_photo(
                season_image,
                update,
                f"#{data['id']}_season_{data_season['season_number']} - <b>{data_season['name']}</b>\n\n{data_season['air_date']}\n\n{data_season['overview']}\n\n",
            )
            delete_file(season_image)

            for episode in data_season["episodes"]:
                sleep(1)
                send_message(
                    f"#{data['id']}_episode_{episode['episode_number']}\n\n<b>{episode['name']}</b>\n{episode['air_date']}\n\nID {episode['id']}\n",
                    update,
                )
                sleep(1)
                # dormir


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

def post(media_type: str, file_path: str, update, context):
    data = read_file(media_type, file_path)

    # url_image = f"{URL_IMAGE}{data['poster_path']}"
    id_themoviedb = data["id"]
    original_title = str(data.get("original_title"))
    tilte = str(data.get("title") or data.get("name"))
    year = data.get("release_date") or data.get("first_air_date", [])[:4]

    msg = f'<b>{original_title} ({year})</b>\n<i>{tilte}</i>\n<a href="https://www.themoviedb.org/{media_type}/{id_themoviedb}">themoviedb</a>'

    image = download_url(f"{data['poster_path']}")
    send_photo(image, update, msg)


def get_link(update) -> str:
    args: list[str] = update.message.text.split(" ")

    try:
        link = args[1]
        LOGGER.info("Se obtuvo correctamente el enlace!")
    except IndexError:
        link = ""
        LOGGER.info("No se obtuvo el enlace!")

    if link != "":
        LOGGER.info(link)
    link = link.strip()
    reply_to = update.message.reply_to_message

    if reply_to is not None:
        LOGGER.info("Se esta intentando obtener el enlace de un mensaje de respuesta!")
        file = None
        media_array = [
            reply_to.document,
            reply_to.video,
            reply_to.audio,
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
            reply_text = reply_to.caption_entities[2]["url"]
            if is_themoviedb_url(reply_text):
                link = reply_text
                LOGGER.info("Se encontro un enlace en el caption!")

    return link


def post_info(update, context):
    link = get_link(update)

    try:
        media_type, file_path = link.split("/")[-2:]
        LOGGER.info(
            "Se obtuvo correctamente el tipo de media y el directorio del archivo!"
        )

        posst(media_type, file_path, update, context)

    except IndexError:
        print("Ocurrió un error de índice al dividir el enlace")
    except Exception as e:
        print("Ocurrió una excepción:", e)


def load_data(update, is_movie):
    link = get_link(update)

    media_type = "movie" if is_movie else "tv"

    if is_valid_link(link):
        msg = send_message(f"<b>Scrapeando:</b> <code>{link}</code>", update)
        data_scrap = scrap_url(link)
        print(data_scrap)
        _id = data_scrap["id"]
        tile = data_scrap["title"]["rendered"]
        return
        tmdb = TheMovieDB(data_scrap["original_title"], data_scrap["release_date"])

        data_media = tmdb.search_movies() if is_movie else tmdb.search_tv_shows()

        if data_media:
            file_name = download_url(data_scrap["imagen"], is_poster=False)
            text = f'<b>{data_scrap["original_title"]}</b>\n<i>{data_scrap["titulo"]}</i>\n<a href="https://www.themoviedb.org/{media_type}/{data_media["id"]}">themoviedb</a>'
            send_photo(file_name, update, text)
            create_file(f'{media_type}/{data_media["id"]}.json', data_media)
            delete_file(file_name)

            # if not is_movie:
            #     for season in data_media["seasons"]:
            #         if season["season_number"] == 0:
            #             continue
            #         LOGGER.info(f"Season: {season['season_number']}")

            #         season_image = download_url(f"{URL_IMAGE}{season['poster_path']}")
            #         data_season = tmdb.search_season_tv_shows(season['season_number'])
            #         sleep(4)
            #         file_name = f'{media_type}/{data_season.get("_id", "temp")}.json'
            #         create_file(file_name, data_season)
            #         # print(data_season)
            #         break

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


list_results = []
pages = 0
STATUS_LIMIT = 25
COUNT = 0
PAGE_NO = 1

tmdb_t = ""


def send_page_no(update, context):
    buttons = ButtonMaker()
    # buttons.sbutton("Movie", "movie")
    # buttons.sbutton("TV Show", "tv")
    buttons.sbutton("Previous", "pre")
    buttons.sbutton("Close", "clo")
    buttons.sbutton("Next", "nex")
    buttons.sbutton("Select", "sel")
    reply_markup = InlineKeyboardMarkup(
        buttons.build_menu(3), footer_buttons=buttons.build_menu(1)
    )

    return reply_markup


def search_movie(update, context):
    args: list[str] = update.message.text.split(" ")
    title = " ".join(args[1:])

    global tmdb_t, list_results, COUNT, PAGE_NO, pages
    tmdb_t = TheMovieDB(title, "")
    tmdb_t.setGetResults(True)
    data_media = tmdb_t.search_movies()

    if data_media:
        list_results = data_media["data"]
        pages = len(list_results)
        dt_p = list_results[PAGE_NO - 1]
        mk = send_page_no(update, context)
        file_name = download_url(f'{dt_p["poster_path"]}')
        title = dt_p["original_title"]
        year = dt_p["release_date"]

        # sendMarkup(file_name, f'{dt_p["original_title"]}', update, mk)
        send_photo(file_name, update, f"{title} ({year})", reply_markup=mk)
        if not PAGE_NO >= pages:
            LOGGER.info(f"Se reliza pre descarga de la imagen {PAGE_NO + 1}")
            download_url(f'{list_results[PAGE_NO]["poster_path"]}')

    else:
        print("No se encontraron resultados.")
        return None


def select(update, context):
    global COUNT, PAGE_NO, list_results
    query = update.callback_query
    query.answer()
    tmdb_t.setId(list_results[PAGE_NO - 1]["id"])
    tmdb_t.setGetResults(False)
    data_media = tmdb_t.search_movies()
    create_file(f'movie/{data_media["id"]}.json', data_media)

    post("movie", data_media["id"], update, context)
    #reset values global
    list_results = []
    # pages = 0
    # STATUS_LIMIT = 25
    COUNT = 0
    PAGE_NO = 1

    # query.edit_message_text(text=f"Selected option: {query.data}")
    return 0


def close(update, context):
    query = update.callback_query
    query.answer()
    query.delete_message()
    return 0


def flip(update, context):
    query = update.callback_query
    query.answer()
    global COUNT, PAGE_NO, list_results
    print(f"COUNT: {COUNT} PAGE_NO: {PAGE_NO}")
    print(f"pages: {pages} STATUS_LIMIT: {STATUS_LIMIT}")
    print(f"list_results: {len(list_results)}")
    if query.data == "nex":
        if PAGE_NO == pages:
            COUNT = 0
            PAGE_NO = 1
        else:
            COUNT += STATUS_LIMIT
            PAGE_NO += 1
    elif query.data == "pre":
        if PAGE_NO == 1:
            COUNT = STATUS_LIMIT * (pages - 1)
            PAGE_NO = pages
        else:
            COUNT -= STATUS_LIMIT
            PAGE_NO -= 1
    # message_utils.update_all_messages()
    # update this mensage
    # query.edit_message_text(text=f"Selected option: {query.data} {COUNT} {PAGE_NO}")
    #  update message with new page number
    mk = send_page_no(update, context)
    dt_p = list_results[PAGE_NO - 1]
    if dt_p["poster_path"] is None:
        file_name = NO_IMAGE
    else:
        file_name = download_url(f'{dt_p["poster_path"]}')

    tl = dt_p["original_title"]
    year = dt_p["release_date"]

    query.edit_message_media(
        media=InputMediaPhoto(
            media=Path(file_name).open("rb"),
            caption=f"{tl} ({year})",
        ),
        reply_markup=mk,
    )

    # query.edit_message_media(
    #     media=InputMediaPhoto(
    #         media=f'{URL_IMAGE}{dt["data"][PAGE_NO - 1]["poster_path"]}',
    #         caption=f'{dt["data"][PAGE_NO - 1]["original_title"]}',
    #     ),
    #     reply_markup=mk,
    # )
    return PAGE_NO

    return 0


def main():
    start_handler = CommandHandler("start", start, pass_args=True, run_async=True)
    post_movie_handler = CommandHandler("movie", post_movie)
    post_tv_handler = CommandHandler("show", post_tv)
    post_info_handler = CommandHandler("info", post_info)
    ping_handler = CommandHandler(
        "ping",
        ping,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    send_log_handler = CommandHandler("log", send_log)
    # start_handler = CommandHandler("start", start, pass_args=True)

    # upd_dis = updater.dispatcher

    upd_dis.add_handler(start_handler)
    upd_dis.add_handler(post_movie_handler)
    upd_dis.add_handler(post_tv_handler)
    upd_dis.add_handler(post_info_handler)
    upd_dis.add_handler(ping_handler)
    upd_dis.add_handler(send_log_handler)
    upd_dis.add_handler(CommandHandler("search", search_movie, pass_args=True))
    next_handler = CallbackQueryHandler(flip, pattern="nex", run_async=True)
    previous_handler = CallbackQueryHandler(flip, pattern="pre", run_async=True)
    select_handler = CallbackQueryHandler(select, pattern="sel", run_async=True)
    close_handler = CallbackQueryHandler(close, pattern="clo", run_async=True)

    upd_dis.add_handler(next_handler)
    upd_dis.add_handler(previous_handler)
    upd_dis.add_handler(select_handler)
    upd_dis.add_handler(close_handler)
    #
    # IGNORE_PENDING_REQUESTS = False
    LOGGER.info("Using long polling.")
    updater.start_polling(read_latency=4)
    # updater.start_polling(timeout=15, read_latency=4)
    # updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)

    LOGGER.info("Bot Started!")

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: ")
    make_folder("tv")
    make_folder("movie")
    make_folder("poster")

    main()

    # print(read_file('movie', '884605'))
    # posst("tv", 1396, update, context)

    # read_file('tv', '615')
    # tmdb = TheMovieDB("Cars", "2006-06-08")
    # tmdb = TheMovieDB("O Amor Dá Voltas", "2022-12-22")
    # tmdb = TheMovieDB("Hounded", "2022-10-21")

    # tmdb.search_movies()
    # print(tmdb.search_movies())

    # tmdb = TheMovieDB("Adventure Time", "2010-04-05")
    # # tmdb = TheMovieDB("Sex Education", "2019-01-11")
    # # print(tmdb.search_tv_shows())
    # tmdb.search_tv_shows()
    # data_media = tmdb.search_season_tv_shows(1)
    # create_file(f'tv/{data_media["_id"]}.json', data_media)

    # create_file('movies/test.txt')
    # data_scrap = scrap_url('https://www.latinomegahd.net/futurama-serie-de-tv-temporada-10-2013-latino-hd-dsnp-web-dl-1080p/')
    # print(scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/'))
    # data_scrap = scrap_url('https://www.latinomegahd.net/amenaza-bajo-el-agua-no-podras-escapar-2020-latino-hd-brrip-1080p/')
    # data_scrap = scrap_url('https://www.latinomegahd.net/sonrie-2022-latino-ultrahd-hdr-bdremux-2160p/')
    # tmdb = TheMovieDB(data_scrap["original_title"], data_scrap["release_date"])
    # tmdb.search_movies()
    # create_file(f'movie/884605.json')

# TODO: CRear boton para cerrar el bot enviar los logs
