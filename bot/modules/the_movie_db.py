import requests
import json
# from urllib.parse import quote_plus

from bot import (
    ACCESS_TOKEN_AUTH,
    LANGUAGE,
    SEARCH_NAME_MOVIE,
    SEARCH_ID_MOVIE,
    SEARCH_ID_TV,
    SEARCH_NAME_TV,
    URL_THEMOVIEDB,
    LOGGER,
)


class TheMovieDB:
    def __init__(self, title: str, release_date: str) -> None:
        self.title = title
        self.release_date = release_date
        self.id: int | None = None
        self.language: str = LANGUAGE[0]
        self.get_resutls: bool = False

    def setId(self, id):
        self.id = id

    def setResults(self, get_resutls):
        self.get_resutls = get_resutls

    def setLanguage(self, language):
        self.language = language

    def exist_overview(self, overview: str) -> bool:
        return bool(overview)

    def _get_search_results(
        self, search_name=None, search_id=None, season=None
    ) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": ACCESS_TOKEN_AUTH,
        }
        payload = {
            # Search id
            "append_to_response": "external_ids",
            # Search name
            "query": self.title,
            "include_adult": "true",
            # "&primary_release_year=2006&page=1"
            "language": self.language,
        }
        _url = f"{URL_THEMOVIEDB}{search_name or search_id}"

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
            print(_url)
            LOGGER.info("Se realizo la solicitud: " + _url)
            LOGGER.info("Datos enviados:")
            LOGGER.info(json.dumps(payload, ensure_ascii=False, indent=4))
            response.raise_for_status()

            if (
                search_id
                and not season
                and not self.exist_overview(response.json().get("overview"))
            ):
                self.setLanguage(LANGUAGE[1])
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
        if self.get_resutls:
            return {"data": response["results"]}

        for result in response["results"]:
            if not result.get("release_date"):
                result["release_date"] = "0000-00-00"

            get_title = result.get(
                "original_title"
                if search_name == SEARCH_NAME_MOVIE
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
        if not self.id and search_name == SEARCH_NAME_TV:
            if response["results"][0]["original_name"]:
                self.id = response["results"][0]["id"]
                LOGGER.info(
                    f"Se encontro el ID: {self.id}, el la primera coincidencia, ya que la validaciona anterior no fue exitosa."
                )

        if self.id:
            return self._get_search_results(
                search_id=SEARCH_ID_MOVIE
                if search_name == SEARCH_NAME_MOVIE
                else SEARCH_ID_TV
            )
        return {}

    def search_movies(self) -> dict:
        return self._search(SEARCH_NAME_MOVIE)

    def search_tv_shows(self) -> dict:
        return self._search(SEARCH_NAME_TV)

    def search_season_tv_shows(self, season: int):
        return self._get_search_results(search_id=SEARCH_ID_TV, season=season)
