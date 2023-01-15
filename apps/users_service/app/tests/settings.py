import requests


PROTOCOL = "http://"

BASE_URL = f"{PROTOCOL}127.0.0.1:8000/api/v1"


class ExtendedRequest:

    @classmethod
    def make_get(cls, url: str, data: dict = None, json: dict = None, headers: dict = None) -> requests.Response:
        return requests.get(url=cls.__build_url(url), data=data, json=json, headers=headers)

    @classmethod
    def make_post(cls, url: str, data: dict = None, json: dict = None, headers: dict = None) -> requests.Response:
        return requests.post(url=cls.__build_url(url), data=data, json=json, headers=headers)

    @classmethod
    def make_patch(cls, url: str, json: dict = None, headers: dict = None):
        return requests.patch(url=cls.__build_url(url), json=json, headers=headers)

    @classmethod
    def make_delete(cls, url: str, headers: dict = None):
        return requests.delete(url=cls.__build_url(url), headers=headers)

    @staticmethod
    def __build_url(url: str) -> str:
        return f"{BASE_URL}/{url}" if not PROTOCOL in url else url
