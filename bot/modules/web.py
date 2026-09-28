import json
import math
from pathlib import Path

import requests
from bs4 import BeautifulSoup  # type:ignore
from tqdm import tqdm  # type:ignore

from .. import LOGGER, exit
from ..core.config_manager import Config


def scrap_paste(url) -> str:
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

    div = soup.find("div", {"class": "content-wrapper"})
    # print(div)
    title = soup.find("h2")
    # print(title.text.strip())
    return title.text.strip()


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


def download_url(url: str | None, is_poster: bool = True):
    if url is None:
        return Config.NO_IMAGE
    if is_poster:
        url = Config.URL_IMAGE + url
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
    return Config.HOST in url


def is_themoviedb_url(url: str):
    return "themoviedb.org" in url
