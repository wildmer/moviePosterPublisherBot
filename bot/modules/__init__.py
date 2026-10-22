# import codecs
import asyncio
import json

# import os
# import unicodedata
# from typing import List, Optional
from pathlib import Path
from time import sleep, time

# import telegram
# from telegram import (  # ReplyKeyboardMarkup,; ReplyKeyboardRemove,; Update,; InlineKeyboardButton,; ParseMode
#     InlineKeyboardMarkup, InputMediaPhoto)
from telegram import InlineKeyboardMarkup, InputMediaPhoto, MessageOriginChannel, Update
from telegram.ext import (  # ConversationHandler,; MessageHandler,;
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

from bot import LOGGER, db, log_filename

from ..core.config_manager import Config

Config.load()
# from bot.Config import HOST, NO_IMAGE, URL_IMAGE
# from bot.helpers.helper_funcs.filters import CustomFilters
# from telegram.ext.utils.promise import CallbackContext
from urllib.parse import urlparse

from bot.helpers.telegram_helper.button_build import ButtonMaker

# from bot.helpers.telegram_helper.decorators import is_authorised
from bot.helpers.telegram_helper.msg_utils import (  # sendMarkup,
    delete_message,
    edit_message,
    send_file,
    send_message,
    send_photo,
)

from .the_movie_db import TheMovieDB
from .web import (
    download_url,
    is_themoviedb_url,
    is_valid_link,
    scrap_paste,
    scrap_url,
)


def escape_markdown(text: str, version: int = 2) -> str:
    if version == 1:
        to_escape = r"_`["
    elif version == 2:
        to_escape = r"_*[]()~`>#+-=|{}.!"
    else:
        raise ValueError("version must be 1 or 2")

    return "".join(["\\" + c if c in to_escape else c for c in text])


tmdb = None

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





async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Function to measure the response time of the bot.

    Args:
        update: The update object containing information about the incoming message.
        context: The context object containing additional information.

    Returns:
        None
    """
    start_time = round(time() * 1000)

    reply = await send_message(update, context, "Pong!")
    end_time = round(time() * 1000)

    # edit_message(f"{end_time - start_time} ms", reply)
    await edit_message(context, reply, text=f"{end_time - start_time} ms")


# TODO: Revisar y havcer que envie los logs segun la fecha
async def send_log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Function to send the log file to the user.

    Args:
        update: The update object containing information about the incoming message.
        context: The context object containing additional information.

    Returns:
        None
    """
    log_file = log_filename
    await send_file(update, context, log_file)


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
        msg = f"{msg}\nTemporadas: {data['number_of_seasons']} Episodios: {data['number_of_episodes']}\n"
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
            file_name = f"tv/{data_season.get('_id', 'temp')}.json"
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


async def post(
    media_type: str, file_path: str, update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    data : dict = read_file(media_type, file_path)

    # url_image = f"{URL_IMAGE}{data['poster_path']}"
    id_themoviedb : int = data["id"]
    original_title = str(data.get("original_title") or data.get("original_name"))
    tilte = str(data.get("title") or data.get("name"))
    year : str = data.get("release_date") or data.get("first_air_date", [])

    url_tmdb = f"https://www.themoviedb.org/{media_type}/{id_themoviedb}"
    msg = f'<b>{original_title} ({year[:4]})</b>\n<i>{tilte}</i>\n<a href="{url_tmdb}">themoviedb</a>'

    msg : str = escape_markdown(msg, version=1)
    image = download_url(f"{data['poster_path']}")
    msg_result = await send_photo(
        update, context, image, msg, parse_mode="HTML", chat_id=Config.CHANNEL_ID
    )
    LOGGER.info(
        f"Se publico {media_type}/{id_themoviedb} correctamente el mensaje con id: {msg_result.message_id} y chat_id: {msg_result.chat_id}"
    )
    # return
    # print("POST ID:", msg_result)
    # discussion = await context.bot.get_chat(chat_id=msg_result.chat.id)
    # try:
    #     chat = await context.bot.get_chat(msg_result.chat.id)
    #     print(chat)
    # except Exception as e:
    #     LOGGER.error(f"Error al obtener el chat: {e}")
    #     return
    # print("CHANNEL ID:", chat.id)
    # print("LINKED CHAT ID:", chat.linked_chat_id)

    # discussion = await context.bot._post(
    #     "getDiscussionMessage",
    #     data={
    #         "chat_id": msg_result.chat.id,
    #         "message_id": msg_result.message_id,
    #     },
    # )
    # print("DISCUSSION:", discussion)
    _ = {
        "id_channel": Config.CHANNEL_ID,
        "type": str(msg_result.chat.type), # "channel",
        "name": msg_result.chat.title or "",
        "channel_message_id": msg_result.message_id,
    }
    db.save_data("chats", _["id_channel"], _["type"], _["name"])

    genres = data["genres"]
    external_ids = data["external_ids"]

    number_of_seasons = ''
    number_of_episodes = ''
    runtime = "runtime, "

    values = [
        data["id"],
        media_type,
        original_title,
        tilte,
        data["original_language"],
        data["tagline"],
        year,
        data["overview"],
        data["vote_average"],
        data["vote_count"]
    ]

    if media_type not in ("movie", "tv"):
        LOGGER.warning("No es tv o movie")
        return
    elif  media_type == 'movie':
        values.insert(8, data["runtime"])
    elif media_type == 'tv':
        number_of_seasons = "number_of_seasons, "
        number_of_episodes = "number_of_episodes, "
        runtime = ''

        values.insert(8, data["number_of_episodes"])
        values.insert(8, data["number_of_seasons"])

    params = ""
    size = len(values)
    if size >= 1:
        params = "?, " * (size - 1)

    total_params = params + "?"

    sql = f"""INSERT INTO titles ( id, media_type, original_title, title, original_language, tagline, release_date, overview, {runtime} {number_of_seasons} {number_of_episodes} vote_average, vote_count ) VALUES ({total_params})"""
    db.execute_query(sql, values)

    for g in genres:
        db.save_data("genres", g["id"], g["name"])
        db.save_data("title_genres", data["id"], g["id"])

    for ex in external_ids.items():
        db.save_data("external_ids", data["id"], ex[0], ex[1])

    sql = f"SELECT p.id FROM posts p WHERE p.channel_chat_id = {_['id_channel']} AND p.channel_message_id = {_['channel_message_id']} AND p.discussion_chat_id = '' AND p.discussion_message_id  = '';"
    try:
        p_id = db.execute_query(sql).fetch_one()[0]
    except:
        p_id = None
        LOGGER.info("no id de post")

    if p_id:
        sql = f"""UPDATE posts SET title_id = {id_themoviedb} WHERE id = {p_id};"""
    else:
        sql = f"""INSERT INTO posts ( channel_chat_id, channel_message_id, title_id ) VALUES ({_["id_channel"]}, {_["channel_message_id"]}, {id_themoviedb})"""
    db.execute_query(sql)


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
            create_file(f"{media_type}/{data_media['id']}.json", data_media)
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

        delete_message(msg)

    else:
        send_message("Proporciona un enlace valido", update)


# @is_authorised
def post_movie(update, context):
    load_data(update, True)


# @is_authorised
def post_tv(update, context):
    load_data(update, False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = "waked up😏😏😏"
    await send_message(update, context, msg)


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
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(3))

    return reply_markup


# async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     args: list[str] = update.message.text.split(" ")
#     title = " ".join(args[1:])

#     global tmdb_t, list_results, pages
#     tmdb_t = TheMovieDB(title, "")
#     tmdb_t.setGetResults(True)
#     data_media = tmdb_t.search_movies()

#     if data_media:
#         list_results = data_media["data"]
#         pages = len(list_results)
#         dt_p = list_results[PAGE_NO - 1]
#         mk = send_page_no(update, context)
#         file_name = download_url(f"{dt_p['poster_path']}")
#         title = dt_p["original_title"]
#         year = dt_p["release_date"]

#         # sendMarkup(file_name, f'{dt_p["original_title"]}', update, mk)
#         # send_photo(file_name, update, f"{title} ({year})", reply_markup=mk)
#         msg = escape_markdown(f"{title} ({year})")
#         # print(f"msg: {msg}")
#         await send_photo(
#             update, context, file_name, msg, reply_markup=mk, parse_mode="MarkdownV2"
#         )

#         if not PAGE_NO >= pages:
#             LOGGER.info(f"Se reliza pre descarga de la imagen {PAGE_NO + 1}")
#             download_url(f"{list_results[PAGE_NO]['poster_path']}")

#     else:
#         print("No se encontraron resultados.")


async def select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global COUNT, PAGE_NO, list_results
    query = update.callback_query
    await query.answer()
    tmdb_t.setId(list_results[PAGE_NO - 1]["id"])
    tmdb_t.setGetResults(False)
    data_media = tmdb_t.search_movies()
    create_file(f"movie/{data_media['id']}.json", data_media)

    await post("movie", data_media["id"], update, context)
    # reset values global
    list_results = []
    # pages = 0
    # STATUS_LIMIT = 25
    COUNT = 0
    PAGE_NO = 1

    # query.edit_message_text(text=f"Selected option: {query.data}")
    return 0


# async def close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     await query.answer()
#     await query.delete_message()
#     return 0


# def flip(update, context):
async def flip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    query.answer()
    global COUNT, PAGE_NO
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
    elif query.data == "clo":
        LOGGER.info("Se recetearan los contenedores")
        COUNT = 0
        PAGE_NO = 1
        await query.delete_message()
        return 0
    # message_utils.update_all_messages()
    # update this mensage
    # query.edit_message_text(text=f"Selected option: {query.data} {COUNT} {PAGE_NO}")
    #  update message with new page number
    mk = send_page_no(update, context)
    dt_p = list_results[PAGE_NO - 1]
    if dt_p["poster_path"] is None:
        file_name = Config.NO_IMAGE
    else:
        file_name = download_url(f"{dt_p['poster_path']}")

    tl = dt_p["original_title"]
    if "*" in tl:
        tl = tl.replace("*", "//*")
    year = dt_p["release_date"]

    await query.edit_message_media(
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


send_chat_id = 0
send_message_id = 0
hash = ""


async def get_info_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global send_chat_id, send_message_id, hash
    send_chat_id = update.message.reply_to_message.chat_id
    send_message_id = update.message.reply_to_message.message_id
    text = update.message.reply_to_message.text
    if "latinomegahd" in str(text):
        url = text.split("\n")[0]
        path = url.split("/")[3]
        # data = scrap_url(text)
        print(path)
        # hasattr

        import zlib

        hash = f"#{hex(zlib.crc32(b'path') & 0xFFFFFFFF)}"


files_ids = []
files_list = []


async def save_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message.document is None:
        await send_message(update, context, "No se ha encontrado un archivo")
    file_unique_id = update.message.reply_to_message.document.file_unique_id
    file_id = update.message.reply_to_message.document.file_id
    file_name = update.message.reply_to_message.document.file_name
    file_caption = update.message.reply_to_message.caption
    file_size = update.message.reply_to_message.document.file_size

    if not file_caption:
        file_caption = ""

    my_data = {
        "file_unique_id": file_unique_id,
        "file_id": file_id,
        "file_name": file_name,
        "file_caption": file_caption,
        "file_size": file_size,
        "file_size_MB": file_size / 1024 / 1024,
    }

    if file_unique_id not in files_ids:
        files_ids.append(file_unique_id)
        files_list.append(my_data)
        # print(files_list)


async def show_list_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = ""
    size_list = len(files_list)
    file_size = 0
    file_size_MB = 0
    msg = f"{size_list} archivos guardados"
    for file in files_list:
        print(file["file_name"])
        print(file["file_id"])
        print(file["file_unique_id"])
        file_size += file["file_size"]
        file_size_MB += file["file_size_MB"]
        msg = f"{msg}\n{file['file_name']}"
    msg = f"{msg}\n\nTamaño total: {file_size} bytes\nor {round(file_size_MB, 2)} MB"
    await send_message(update, context, msg)


async def send_list_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file_size = 0
    file_size_MB = 0
    for file in files_list:
        file_size += file["file_size"]
        file_size_MB += file["file_size_MB"]
        text = f"{hash}\n{file['file_caption']}"
        await send_file(
            update,
            context,
            file["file_id"],
            chat_id=send_chat_id,
            reply_to_message_id=send_message_id,
            caption=text,
        )
        await asyncio.sleep(4)
    await send_message(
        update,
        context,
        f"{hash}\nSe han enviado {len(files_list)} archivos con un tamaño total: {file_size} bytes\nor {round(file_size_MB, 2)} MB",
    )


def parse_message(msg):
    _json = msg.to_dict()
    return json.dumps(_json, indent=3, default=str, ensure_ascii=False)


def save_links_in_db(**kwargs):
    title_id = kwargs["title_id"]
    link_origins = kwargs["link_origins"]
    # print(link_origins)
    paste = kwargs["paste"]
    links_cloud = kwargs["links_cloud"]
    # tag = kwargs["tag"]
    msg_for_send = ""

    name_past = scrap_paste(paste)
    if not name_past:
        print("detener")
        exit()

    #  save domain and path
    name_domain = urlparse(link_origins).hostname
    netloc = urlparse(link_origins).netloc
    path = link_origins.split(netloc)[1]
    db.save_data("domains", "origin", netloc, name_domain)
    # netloc = f"'{netloc}'"  # Agregar comillas a la variable netloc
    # get_domain_id = db.get_id(
    #     "domains", "host", netloc
    # )  # agrearcomillas a la columna host
    sql = f"""SELECT d.id FROM domains d WHERE "host" like '{netloc}'"""
    get_domain_id = db.execute_query(sql).fetch_one()
    get_domain_id = get_domain_id[0]

    _id = db.save_data("paths", get_domain_id, path)
    # path = f"'{path}'"  # Agregar comillas a la variable path
    # get_path_id = db.get_id("paths", "path", path)
    sql = f"""SELECT p.id FROM paths p WHERE "path" like '{path}'"""
    get_path_id = db.execute_query(sql).fetch_one()
    get_path_id = get_path_id[0]
    db.save_data(
        "links", title_id, get_path_id, "", columns=["title_id", "path_id", "name"]
    )
    sql = f"""SELECT id FROM links l WHERE l.title_id = {title_id} AND l.path_id = {get_path_id}"""
    _id_origin = db.execute_query(sql)
    _id_origin = _id_origin.fetch_one()[0]
    # empezar a construir el mensaje para enviar al chat de discusion, con el link de origen y el link de paste, y si hay links en la nube, agregarlos tambien
    # esto con formato markdown, con el name domain como texto del link, y el netloc con el path como url del link, y si hay links en la nube, agregarlos tambien con el mismo formato

    # msg_for_send = f"<b>Links:</b>\n"
    msg_for_send += f"<a href='{link_origins}'>{name_domain}</a>\n"

    # save paste
    name_domain, netloc = urlparse(paste).hostname, urlparse(paste).netloc
    path = paste.split(netloc)[1]

    path = paste.split(netloc)[1]
    sql = f"""SELECT p.id FROM paths p WHERE "path" like '{path}'"""
    get_path_id = exist_path_in_bd = db.execute_query(sql).fetch_one()  # may be None

    id_paste = None

    if exist_path_in_bd:
        print(f"el path ya existe {path}")
        id_paste = get_path_id[0]
        # return False
        # & continuaos pero no guardamos, solo obtemos el id
    else:
        # TODO: 345.slidb: al no existir este deberia devolver el id ya que se acaba de guardar
        # ? pero el domain siempre estara lo que debomos revisar es el 'path' table
        # * upate no cambiara
        db.save_data("domains", "paste", netloc, name_domain)  # * save domain.paste
        # netloc = (
        #     f"'{netloc}'"  # TODO eso se puede hacaer #456 in funtion third parameter
        # )

        sql = f"""SELECT d.id FROM domains d WHERE "host" like '{netloc}'"""
        get_domain_id = db.execute_query(sql).fetch_one()
        get_domain_id = get_domain_id[0]
        # get_domain_id = db.get_id(
        #     "domains", "host", netloc
        # )  # ^ delete this line when complete #345.slidb

        _id = db.save_data("paths", get_domain_id, path)
        # path = f"'{path}'"  # TODO eso se puede hacaer #456 in funtion third parameter
        # get_path_id = db.get_id("paths", "path", path)
        sql = f"""SELECT p.id FROM paths p WHERE "path" like '{path}'"""
        get_path_id = db.execute_query(sql).fetch_one()
        get_path_id = get_path_id[0]

        sql = f"""SELECT id FROM links l WHERE l.title_id = {title_id} AND l.path_id = {get_path_id}"""
        # todo: aqui tambien se puede filtrar por parent_id

        if id_paste := db.execute_query(sql).fetch_one():
            # _id_paste = db.execute_query(sql)
            id_paste = id_paste[0]
            print(id_paste)
        else:
            try:
                # ^ en pruebas, pero deberia funcionar
                id_paste = db.save_data(
                    "links",
                    title_id,
                    get_path_id,
                    _id_origin,
                    name_past,
                    columns=["title_id", "path_id", "parent_id", "name"],
                )
            except Exception as e:
                print(str(e))

    # sql = f"""SELECT id FROM links l WHERE l.title_id = {title_id} AND l.path_id = {get_path_id}"""
    # _id_paste = db.execute_query(sql)
    # id_paste = _id_paste.fetch_one()[0]
    # print(id_path)
    # todo no esta registradno los links en parent id # *corregido
    msg_for_send += f"<a href='{paste}'>{name_past}</a>\n\n"

    if links_cloud:
        print(len(links_cloud))
        end_link = links_cloud[-1]
        for link in links_cloud:
            sep = " - " if link != end_link else "\n"
            name_domain = urlparse(link).hostname
            netloc = urlparse(link).netloc
            path = link.split(netloc)[1]
            db.save_data("domains", "cloud", netloc, name_domain)
            # netloc = f"'{netloc}'"  # Agregar comillas a la variable netloc
            # get_domain_id = db.get_id("domains", "host", netloc)
            sql = f"""SELECT d.id FROM domains d WHERE "host" like '{netloc}'"""
            get_domain_id = db.execute_query(sql).fetch_one()
            get_domain_id = get_domain_id[0]

            _id = db.save_data("paths", get_domain_id, path)
            # path = f"'{path}'"  # Agregar comillas a la variable path
            # get_path_id = db.get_id("paths", "path", path)
            sql = f"""SELECT p.id FROM paths p WHERE "path" like '{path}'"""
            get_path_id = db.execute_query(sql).fetch_one()
            get_path_id = get_path_id[0]

            db.save_data(
                "links",
                title_id,
                get_path_id,
                "",
                id_paste,
                columns=["title_id", "path_id", "name", "parent_id"],
            )
            msg_for_send += f"<a href='{link}'>{name_domain}</a>{sep}"

    return msg_for_send


async def add_cloud_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args: list[str] = update.message.text.split("\n")
    # print(parse_message(update.message))
    # msg_forward_origin = 
    # print(up_message)
    # print(msg_forward_origin)
    if msg_forward_origin := update.message.reply_to_message.forward_origin:
        channel_chat_id = msg_forward_origin.chat.id
        extract_message_id = msg_forward_origin.message_id

        if len(args) < 3:
            # await send_message(update, context, "Uso: /edit <message_id> <nuevo_texto>")
            await send_message(
                update,
                context,
                "Uso: /edit <link_origins> <paste> <tag_or_name> [<links_cloud]",
            )
            return
        command = args[0]
        if not command.startswith("/"):
            print("no es coomando")
            return
        link_origins = args[1]
        paste = args[2]
        # name = args[3] if len(args) > 3 else None
        links_cloud = sorted(args[3:]) if len(args[3:]) >= 1 else None

        # sql = f""""""
        print("add_cloud_links")

        sql = f"""
            SELECT
                po.id,
                po.discussion_chat_id,
                po.discussion_message_id,
                po.title_id
            FROM posts AS po
            WHERE po.channel_chat_id = {channel_chat_id}
            AND po.channel_message_id = {extract_message_id};
        """

        row = db.execute_query(sql).fetch_one()
        if not row:
            return
        post_id, chat_id, extract_message_thread_id, title_id = row

        if title_id is not None:
            msg_for_send = save_links_in_db(
                title_id=title_id,
                link_origins=link_origins,
                paste=paste,
                links_cloud=links_cloud,
                # tag=name,
            )

            if not msg_for_send:
                return

            # msg = "waiting..."
            # msg = escape_markdown(msg_for_send, version=1)
            reply = await send_message(
                update,
                context,
                msg_for_send,
                parse_mode="HTML",
                reply_to_message=True,
                reply_to_message_id=extract_message_thread_id,
                reply_to_message_chat_id=chat_id,
            )
            # print("REPLY:", reply)
            discussion_message_id = reply.message_id
            message_thread_id = reply.message_thread_id
            # sql = f"""UPDATE post_items SET bot_message_id = {discussion_message_id} WHERE post_id = {post_id} AND title_id = {title_id};"""
            # ! anadir validacion si existe bot_message_id
            db.save_data(
                "post_messages",
                post_id,
                discussion_message_id,
                "links",
                columns=["post_id", "message_id", "kind"],
            )

            # db.execute_query(sql)
            # return
    return


async def edit_message_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    args: list[str] = update.message.text.split("\n")
    try:
        msg_forward_origin = update.message.reply_to_message.forward_origin
    except:
        msg_forward_origin = None
        print("no es un mensaje reenviado por ende se aplicara la segunda opcion")

    if msg_forward_origin:
        channel_chat_id = msg_forward_origin.chat.id
        extract_message_id = msg_forward_origin.message_id
        sql = f"""SELECT po.id, po.discussion_chat_id, pi.bot_message_id, pi.title_id  FROM posts as po JOIN post_items as pi  ON po.id = pi.post_id  WHERE channel_chat_id = {channel_chat_id} AND channel_message_id = {extract_message_id};"""
        print(sql)
        # _x = db.execute_query(sql).fetch_one()
        # print(_x)
        post_id, chat_id, bot_message_id, title_id = db.execute_query(sql).fetch_one()
    else:
        extract_message_id = update.message.reply_to_message.message_id
        extract_message_thread_id = (
            update.message.reply_to_message.message_thread_id
        )  # root first message id
        chat_id = update.message.reply_to_message.chat_id
        this_message_id = update.message.message_id
        # obtener el title_id de la post_items agregando validaciones en la tabla post, puede ser con un union de la tabla post_items y post, para obtener el title_id de la tabla post_items, con el chat_id y message_id del mensaje de respuesta
        sql = f"""SELECT title_id FROM post_items WHERE post_id = (SELECT id FROM posts WHERE discussion_chat_id = {chat_id} AND discussion_message_id = {extract_message_thread_id});"""
        _x = db.execute_query(sql).fetch_one()
        print(_x)

        if _x is not None:
            title_id = _x[0]
        else:
            print("erro al traer el tilte id ")
            return
    # print(f"title_id: {_x}")

    if len(args) < 3:
        # await send_message(update, context, "Uso: /edit <message_id> <nuevo_texto>")
        await send_message(
            update,
            context,
            "Uso: /edit <link_origins> <paste> <tag_or_name> [<links_cloud]",
        )
        return

    link_origins = args[1]
    paste = args[2]
    name = args[3] if len(args) > 3 else None
    links_cloud = sorted(args[4:]) if len(args[4:]) >= 1 else None
    print(args)

    msg_for_send = save_links_in_db(
        title_id=title_id,
        link_origins=link_origins,
        paste=paste,
        links_cloud=links_cloud,
        tag=name,
    )

    if msg_forward_origin:
        # print(msg_for_send)
        await edit_message(
            context,
            update.message,
            chat_id=chat_id,
            message_id=bot_message_id,
            text=msg_for_send,
            parse_mode="HTML",
        )
    # msg = escape_markdown(msg_for_send, version=1)
    # reply = await send_message(
    #     update,
    #     context,
    #     msg_for_send,
    #     parse_mode="HTML",
    #     reply_to_message=True,
    #     reply_to_message_id=extract_message_thread_id,
    #     reply_to_message_chat_id=chat_id,
    # )
    # print("REPLY:", reply)
    # discussion_message_id = reply.message_id
    # message_thread_id = reply.message_thread_id
    # sql = f"""UPDATE post_items SET bot_message_id = {discussion_message_id} WHERE post_id = {post_id} AND title_id = {title_id};"""
    # db.execute_query(sql)
    else:
        # agreromos los links
        await edit_message(
            context,
            update.message.reply_to_message,
            text=msg_for_send,
            parse_mode="HTML",
        )

    # print(args)
    # print(message_id)
    # from pprint import pprint
    # # pprint(vars(update.message))
    # pprint(parse_message(update.message))
    # txt =str(update.message) #.replace(", ", "\n")
    # print(txt)
    # if len(args) < 3:
    #     await send_message(update, context, "Uso: /edit <message_id> <nuevo_texto>")
    #     return

    # message_id = int(args[1])
    # new_text = " ".join(args[2:])

    # try:
    #     await edit_message(context, update.message, new_text)
    #     await send_message(update, context, f"Mensaje editado correctamente: {message_id}")
    # except Exception as e:
    #     LOGGER.error(f"Error al editar el mensaje: {e}")
    #     await send_message(update, context, f"No se pudo editar el mensaje: {message_id}")


async def add_paths(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args: list[str] = update.message.text.split(" ")
    print(args)
    name = urlparse(args[1]).hostname
    netloc = urlparse(args[1]).netloc
    path = args[1].split(netloc)[1]
    if args[2] == "origin":
        db.save_data("domains", "origin", name, netloc)
    elif args[2] == "cloud":
        db.save_data("domains", "cloud", name, netloc)
    else:
        db.save_data("domains", "paste", name, netloc)
    get_domain_id = db.get_name("domains", "name", name)
    _id = db.save_data("paths", get_domain_id, path)
    # send_message(f"- {_id} enviado y guardado")


# async def add_origins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     args: list[str] = update.message.text.split(" ")
#     *_, name = args[1].partition("//")
#     _id = db.save_data("domains", "origin", name, args[1])


async def add_cloud(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # test
    # db.test()
    # db.save_data(
    #     "posts",
    #     -1001713666556,
    #     363,
    #     9798,
    #     columns=["channel_chat_id", "channel_message_id", "title_id"],
    # )
    slq = """UPDATE posts
    SET discussion_chat_id    = -1001911575890,
        discussion_message_id = 5845
    WHERE channel_chat_id    = -1001713666556
    AND channel_message_id = 363;"""

    db.execute_query(slq)
    # print(db.execute_query("PRAGMA table_info(posts)"))
    # print(
    #     db.execute_query("""
    #     SELECT sql
    #     FROM sqlite_master
    #     WHERE type = 'table' AND name = 'posts'
    # """)
    # )
    # args: list[str] = update.message.text.split(" ")
    # *_, name = args[1].partition("//")
    # _id = db.save_data("domains", "cloud", name, args[1])
    # # send_message(f"- {_id} enviado y guardado")


async def clean_list_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global files_list, files_ids
    files_list = []
    files_ids = []
    await send_message(update, context, "Se ha limpiado la lista de archivos")


async def handle_discussion_message(update, context):
    message = update.message

    if not message.is_automatic_forward:
        return

    origin = message.forward_origin

    if not isinstance(origin, MessageOriginChannel):
        return

    channel_id = origin.chat.id
    channel_message_id = post_id = origin.message_id

    discussion_chat_id = message.chat.id
    discussion_message_id = message.message_id
    discussion_title = message.chat.title

    print("POST:", post_id)
    print("CHANNEL:", channel_id)
    print("DISCUSSION CHAT:", discussion_chat_id)
    print("DISCUSSION MESSAGE:", discussion_message_id)
    # print("MESSAGE:", message)
    # id_c = db.get_id("channels", "telegram_id", channel_id)
    # _discussion_chat_id = db.get_id("chats", "telegram_id", discussion_chat_id)
    db.save_data("chats", message.chat.id, "group", discussion_title)
    # post_id = db.get_id("posts", "channel_message_id", channel_message_id)
    slq = f"""UPDATE posts
    SET discussion_chat_id    = {discussion_chat_id},
        discussion_message_id = {discussion_message_id}
    WHERE channel_chat_id    = {channel_id}
    AND channel_message_id = {channel_message_id};"""
    db.execute_query(slq)


#     return
#     # TODO: esta estructura del codigo ya no es necesaria
#     #  ~ el codigo ahora ya no es necesario
#     # db.save_data("posts", channel_id, post_id, discussion_message_id)
#     # sql = f"""SELECT id FROM posts WHERE channel_chat_id = {Config.CHANNEL_ID} AND channel_message_id = {channel_message_id};"""
#     # _x = db.execute_query(sql)

#     # _post_id =  db.fetch_one()[0]

#     title_id = db.get_title_id("post_items", "post_id", post_id)
#     # _post_id = db.get_id(
#     #     "posts", "telegram_post_id", post_id
#     # ) # | agregar validacion extra puede falar
#     # db.save_data("post_items", _post_id,title_id, discussion_message_id) # update

#     # db.save_data("sources", itle_id
#     msg = "waiting..."
#     msg = escape_markdown(msg, version=1)
#     reply = await send_message(
#         update,
#         context,
#         msg,
#         reply_to_message=True,
#         reply_to_message_id=discussion_message_id,
#     )
#     # print("REPLY:", reply)
#     print(discussion_message_id)
#     discussion_message_id = reply.message_id
#     print(discussion_message_id)
#     #  pienso que el envio del mensajhe es innesasario
#     #

#     message_thread_id = reply.message_thread_id
#     sql = f"""UPDATE post_items
#    SET bot_message_id = {discussion_message_id}
#  WHERE post_id = {post_id} AND title_id = {title_id};"""
#     db.execute_query(sql)
#     # , reply_to_message=Message(api_kwargs={'forward_date': 1791009084, 'forward_from_chat': {'id': -1001251251830, 'title': 'Cosas', 'type': 'channel'}, 'forward_from_message_id': 178}
#     # edit_message(f"{end_time - start_time} ms", reply)
#     # await edit_message(context, reply, f"{end_time - start_time} ms")


# # async def handle_channel_post(update, context):
# #     print("w")
# #     post = update.channel_post

# #     print("Canal:", post.chat.id)
# #     print("Post:", post.message_id)
# #     print("Texto:", post.text or post.caption)

STATUS_LIMIT = 25


class MovieSearchHandler:
    def __init__(self):
        # manejar las busquedas en un diccionario
        # dict[word search]=[...]
        # dict[word search two]=[...]
        self.list_results = []
        self.page_no = 1
        self.pages = 0
        self.count = 0
        self.tmdb_t = None
        self.type_media = "movie"

    async def change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.type_media == "movie":
            self.type_media = "tv"
        else:
            self.type_media = "movie"
        await update.message.reply_text(f"Se ha cambiado a {self.type_media}")

    def reset_args(self):
        LOGGER.info("Se restablecieron los argumentos")
        self.list_results = []
        self.page_no = 1
        self.pages = 0
        self.count = 0
        self.tmdb_t = None

    def create_buttons(self):
        buttons = ButtonMaker()
        buttons.sbutton("Previous", "pre")
        buttons.sbutton("Close", "clo")
        buttons.sbutton("Next", "nex")
        buttons.sbutton("Select", "sel")
        return InlineKeyboardMarkup(buttons.build_menu(3))

    async def search_movie(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args: list[str] = update.message.text.split(" ")
        title = " ".join(args[1:])
        self.tmdb_t = TheMovieDB(title, "")
        self.tmdb_t.setGetResults(True)
        if self.type_media == "tv":
            data_media = self.tmdb_t.search_tv_shows()
        else:
            data_media = self.tmdb_t.search_movies()

        if data_media:
            # print(json.dumps(data_media, ensure_ascii=False, indent=4))
            self.list_results = data_media["data"]
            self.pages = len(self.list_results)
            return await self.show_page(update, context, self.page_no)
        else:
            await update.message.reply_text("No se encontraron resultados.")
            return None

    async def show_page(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        page_no: int,
        is_update: bool = False,
    ):
        try:
            self.page_no = page_no
            dt_p = self.list_results[page_no - 1]
            if dt_p["poster_path"] is None:
                print("No se encontro poster")
                print(Path(Config.NO_IMAGE).exists())
                file_name = Config.NO_IMAGE
            else:
                file_name = (
                    download_url(dt_p["poster_path"])
                    if dt_p["poster_path"]
                    else Config.NO_IMAGE
                )
            if self.type_media == "tv":
                title = dt_p["original_name"]
                year = dt_p["first_air_date"]
            else:
                title = dt_p["original_title"]
                year = dt_p["release_date"]

            _id = dt_p["id"]
            # con esto sabemos si ya posteamos la pelicula antes
            sql = f"""SELECT p.channel_message_id FROM posts AS p WHERE p.title_id = (SELECT t.id FROM titles AS t WHERE t.id = {_id}); """
            _id_channel = db.execute_query(sql).fetch_one()
            # print(_id_channel)
            if _id_channel:
                title = escape_markdown(title)
                year = escape_markdown(f"({year})")
                msg = f"[{title}](https://t.me/abzy12/{_id_channel[0]}) {year}"
            else:
                msg = escape_markdown(f"{title} ({year})")
            if not is_update:
                reply_markup = self.create_buttons()
                await send_photo(
                    update,
                    context,
                    file_name,
                    msg,
                    reply_markup=reply_markup,
                    parse_mode="MarkdownV2",
                )
            else:
                query = update.callback_query
                await query.answer()
                await query.edit_message_media(
                    media=InputMediaPhoto(
                        media=Path(file_name).open("rb"),
                        caption=msg,
                        parse_mode="MarkdownV2",
                    ),
                    reply_markup=self.create_buttons(),
                )
            if not self.page_no >= self.pages:
                if self.list_results[self.page_no]["poster_path"] is not None:
                    LOGGER.info(
                        f"Se reliza pre descarga de la imagen {self.page_no + 1}"
                    )
                    download_url(self.list_results[self.page_no]["poster_path"])
        except Exception as e:
            LOGGER.error(f"Error mostrando la página: {e}")

    async def flip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "nex":
            if self.page_no == self.pages:
                self.page_no = 1
                self.count = 0
            else:
                self.count += STATUS_LIMIT
                self.page_no += 1
            # self.page_no = self.page_no + 1 if self.page_no < self.pages else 1
        elif query.data == "pre":
            if self.page_no == 1:
                self.count = STATUS_LIMIT * (self.pages - 1)
                self.page_no = self.pages
            else:
                self.count -= STATUS_LIMIT
                self.page_no -= 1
            # self.page_no = self.page_no - 1 if self.page_no > 1 else self.pages
        elif query.data == "clo":
            self.reset_args()
            await query.delete_message()
            return

        await self.show_page(update, context, self.page_no, is_update=True)

    async def select(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        selected_movie = self.list_results[self.page_no - 1]
        self.tmdb_t.setId(selected_movie["id"])
        self.tmdb_t.setGetResults(False)
        if self.type_media == "tv":
            data_media = self.tmdb_t.search_tv_shows()

            create_file(f"tv/{data_media['id']}.json", data_media)
            await post("tv", data_media["id"], update, context)
            # print season for season in data_media["seasons"]
        else:
            data_media = self.tmdb_t.search_movies()

            create_file(f"movie/{data_media['id']}.json", data_media)
            await post("movie", data_media["id"], update, context)
