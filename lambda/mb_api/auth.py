import requests
from mb_api.constants import MB_API_URL

class MbAuthenticator:
    def __init__(self,
                 login: str,
                 password: str):

        self.__login = login
        self.__password = password

    @property
    def access_token(self):
        r = requests.post(
            url=f'{MB_API_URL}/v4/authorize',
            data={'login': self.__login,'password': self.__password},
            timeout=5
        )
        r.raise_for_status()
        return r.json()["access_token"]

