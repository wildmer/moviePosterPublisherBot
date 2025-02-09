import json
import time

import requests

from bot import LOGGER, config

# from urllib.parse import quote_plus


class TheMovieDB:
    def __init__(self, title: str, release_date: str) -> None:
        self.title = title
        self.release_date = release_date
        self.id: int | None = None
        self.language: int = 0
        self.get_results: bool = False

    def setId(self, id):
        self.id = id

    def setGetResults(self, get_results: bool) -> None:
        """Set the value of get_results, if True, the method will return the results of the search, if False, it will return the details of the search"""
        self.get_results = get_results

    def setLanguage(self, language: int) -> None:
        size = len(config.LANGUAGE)
        if language < 0 or language >= size:
            raise Exception(f"El idioma {language} no es valido")
        self.language = language

    def exist_overview(self, overview: str) -> bool:
        return bool(overview)

    def _get_search_results(
        self, search_name=None, search_id=None, season=None
    ) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": config.ACCESS_TOKEN_AUTH,
        }
        payload = {
            # Search id
            "append_to_response": "external_ids",
            # Search name
            "query": self.title,
            "include_adult": "true",
            # "&primary_release_year=2006&page=1"
            "language": config.LANGUAGE[self.language],
        }
        _url = f"{config.URL_THEMOVIEDB}{search_name or search_id}"

        if search_name:
            payload.pop("append_to_response")

        if search_id or season:
            _url = f"{_url}{self.id}"
            payload.pop("query")
            payload.pop("include_adult")
            if season:
                _url = f"{_url}/season/{season}"

        try:
            response = requests.get(_url, headers=headers, params=payload)
            LOGGER.info("Se realizo la solicitud: " + _url)
            LOGGER.info("Datos enviados:")
            LOGGER.info(json.dumps(payload, ensure_ascii=False, indent=4))
            LOGGER.info(response.raise_for_status())
            print(response.status_code)

            if (
                search_id
                and not season
                and not self.exist_overview(response.json().get("overview"))
            ):
                LOGGER.info(
                    f"La descripción no existe en el idioma {config.LANGUAGE[self.language]}, se intentará con el siguiente idioma."
                )
                # se realizara una espera de 5 segundos para evitar el bloqueo de la API
                time.sleep(5)
                self.setLanguage(self.language + 1)
                # en caso de que siga presentando el mismo problema, se debera de eliminara el parametro de idioma
                return self._get_search_results(search_name, search_id)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en la solicitud: {e}")

    def _search(self, search_name: str) -> dict:
        response = self._get_search_results(search_name)

        if not (response and response["total_results"] != 0):
            LOGGER.info(
                f"No es una {search_name.lower()} o está escrita de manera incorrecta"
            )
            return {}
        if self.get_results:
            return {"data": response["results"]}

        for result in response["results"]:
            if not result.get("release_date"):
                result["release_date"] = "0000-00-00"

            get_title = result.get(
                "original_title"
                if search_name == config.SEARCH_NAME_MOVIE
                else "original_name"
            )
            print(
                get_title,
                "->",
                self.title,
                self.release_date,
                result.get("first_air_date"),
                result.get("release_date"),
            )
            if get_title.lower() == self.title.lower() and (
                self.release_date == result.get("first_air_date")
                or self.release_date == result.get("release_date")
                or self.release_date[:4] == result.get("release_date")[:4]
            ):
                self.id = result["id"]
                LOGGER.info(f"Se encontro el ID: {self.id}")
                break
        if not self.id and search_name == config.SEARCH_NAME_TV:
            if response["results"][0]["original_name"]:
                self.id = response["results"][0]["id"]
                LOGGER.info(
                    f"Se encontro el ID: {self.id}, el la primera coincidencia, ya que la validaciona anterior no fue exitosa."
                )

        if self.id:
            return self._get_search_results(
                search_id=config.SEARCH_ID_MOVIE
                if search_name == config.SEARCH_NAME_MOVIE
                else config.SEARCH_ID_TV
            )
        return {}

    def search_movies(self) -> dict:
        return self._search(config.SEARCH_NAME_MOVIE)

    def search_tv_shows(self) -> dict:
        return self._search(config.SEARCH_NAME_TV)

    def search_season_tv_shows(self, season: int):
        return self._get_search_results(search_id=config.SEARCH_ID_TV, season=season)
