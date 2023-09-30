import requests
import json
# from urllib.parse import quote_plus
from bot import ACCESS_TOKEN_AUTH, LANGUAGE, SEARCH_NAME_MOVIE, SEARCH_ID_MOVIE, SEARCH_ID_TV, SEARCH_NAME_TV, URL_THEMOVIEDB, LOGGER


class TheMovieDB:
    def __init__(self, title: str, release_date: str) -> None:
        self.title = title
        self.release_date = release_date
        self.ID: int = None

    def _get_search_results(self, search_name=None, search_id=None) -> dict:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': ACCESS_TOKEN_AUTH
        }
        payload = {
            # Search id
            'append_to_response': 'external_ids',
            # Search name
            'query': self.title, 'include_adult': 'true',
            # "&primary_release_year=2006&page=1"
            'language': LANGUAGE
        }
        _url = f"{URL_THEMOVIEDB}{search_name or search_id}"

        if search_name:
            payload.pop("append_to_response")

        if search_id:
            _url = f"{_url}{self.ID}"
            payload.pop("query")
            payload.pop("include_adult")

        try:
            response = requests.get(_url, headers=headers, params=payload)
            LOGGER.info("Se realizo la solicitud: " + _url)
            LOGGER.info("Datos enviados:")
            LOGGER.info(json.dumps(payload, ensure_ascii=False, indent=4))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en la solicitud: {e}")

    def _search(self, search_name: str) -> dict:
        response = self._get_search_results(search_name)

        if not (response and response["total_results"] != 0):
            LOGGER.info(
                f"No es una {search_name.lower()} o está escrita de manera incorrecta")
            return None

        for result in response["results"]:
            if not result.get("release_date"):
                result["release_date"] = "0000-00-00"

            get_title = result.get(
                "original_title" if search_name == SEARCH_NAME_MOVIE else "original_name"
            )
            if get_title.lower() == self.title.lower() and (
                self.release_date == result.get("first_air_date")
                or self.release_date == result.get("release_date")
                or self.release_date[:4] == result.get("release_date")[:4]
            ):
                self.ID = result["id"]
                LOGGER.info(f"Se encontro el ID: {self.ID}")
                break

        # if (response["results"][0]("original_name")):
        #     self.ID = response["results"][0]["id"]
        #     LOGGER.info(f"Se encontro el ID: {self.ID}, el la primera coincidencia")
            

        if self.ID:
            return self._get_search_results(search_id=SEARCH_ID_MOVIE if search_name == SEARCH_NAME_MOVIE else SEARCH_ID_TV)
        return None

    def search_movies(self) -> dict:
        return self._search(SEARCH_NAME_MOVIE)

    def search_tv_shows(self) -> dict:
        return self._search(SEARCH_NAME_TV)
