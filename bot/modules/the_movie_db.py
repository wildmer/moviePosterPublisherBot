import requests
from urllib.parse import quote_plus
from bot import ACCESS_TOKEN_AUTH, LANGUAGE, SEARCH_NAME_MOVIE, SEARCH_ID_MOVIE, SEARCH_ID_TV, SEARCH_NAME_TV, URL_THEMOVIEDB


class TheMovieDB:
    def __init__(self, title: str, release_date: str) -> None:
        self.title = title
        self.release_date = release_date
        self.ID: int = None

    def _get_search_results(self, search_name=None, search_id=None) -> dict:
        headers = {'Authorization': ACCESS_TOKEN_AUTH}
        payload = {
            # Search id
            'append_to_response': 'external_ids',
            # Search name
            'query': quote_plus(self.title), 'include_adult': 'true',
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
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en la solicitud: {e}")

    def _search(self, search_name: str) -> dict:
        response = self._get_search_results(search_name)

        if not (response and response["total_results"] != 0):
            print(
                f"No es una {search_name.lower()} o está escrita de manera incorrecta")
            return None

        for result in response["results"]:
            if not result.get("release_date"):
                result["release_date"] = "0000-00-00"

            if result.get(
                "original_title" if search_name == SEARCH_NAME_MOVIE else "original_name"
            ) == self.title and (
                self.release_date == result.get("first_air_date")
                or self.release_date == result.get("release_date")
                or self.release_date[:4] == result.get("release_date")[:4]
            ):
                self.ID = result["id"]
                break

        if self.ID:
            return self._get_search_results(search_id=SEARCH_ID_MOVIE if search_name == SEARCH_NAME_MOVIE else SEARCH_ID_TV)
        return None

    def search_movies(self) -> dict:
        return self._search(SEARCH_NAME_MOVIE)

    def search_tv_shows(self) -> dict:
        return self._search(SEARCH_NAME_TV)
