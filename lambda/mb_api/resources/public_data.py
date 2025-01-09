from mb_api.api_handler import MbApiHandler
from mb_api.auth import MbAuthenticator


class PublicData(MbApiHandler):
    def __init__(self,
                 mb_auth: MbAuthenticator):
        super().__init__(mb_auth=mb_auth)


    def list_tickers(self,
                     symbols: list) -> dict:
        r = self.handle_request(
            method='GET',
            endpoint=f'/v4/tickers',
            params={'symbols': ','.join(symbols)},
            authenticated=False,
            timeout=2.5,

        )
        return r.json()

    def list_candles(self,
                     symbol: str,
                     resolution: str,
                     to_timestamp: int,
                     from_timestamp: int = None,
                     countback: int = None
                     ):

        r = self.handle_request(
            method='GET',
            endpoint=f'/v4/candles',
            params = {
                'symbol': symbol,
                'resolution': resolution,
                'to': to_timestamp,
                **({'from': from_timestamp} if from_timestamp else {}),
                **({'countback': countback} if countback else {}),
            },
            authenticated=False,
            timeout=2.5,
        )
        return r.json()
