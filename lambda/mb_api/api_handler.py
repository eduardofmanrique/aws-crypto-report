from mb_api.auth import MbAuthenticator
from mb_api.constants import MB_API_URL
import requests

class MbApiHandler:
    def __init__(self,
                 mb_auth: MbAuthenticator):
        self.__mb_auth = mb_auth

    def handle_request(self,
                method: str,
                endpoint: str,
                authenticated: bool = False,
                **kwargs) -> requests.request:
        accepted_methods = ['GET']
        if method not in accepted_methods:
            raise Exception(f'Request method {method} is not accepted. '
                            f'Only {", ".join(accepted_methods)} are allowed')
        attempt = 0
        while attempt < 5:
            try:
                url = f'{MB_API_URL}{endpoint}'
                print(f'[{method}] {url} - starting...')
                r = requests.request(
                    method=method,
                    url=url,
                    headers=None if not authenticated else {
                        'Authorization': f'Bearer {self.__mb_auth.access_token}'
                    },

                    **kwargs
                )
                r.raise_for_status()
                print(f'[{method}] {url} - 200')
                return r
            except requests.exceptions.ReadTimeout:
                print(f'Attempt n {attempt}')
                attempt += 1
        raise Exception('There might be an connection error')

