from mb_api.api_handler import MbApiHandler
from mb_api.auth import MbAuthenticator


class Account(MbApiHandler):
    def __init__(self,
                 mb_auth: MbAuthenticator):
        super().__init__(mb_auth=mb_auth)
        self.resource_name = 'accounts'


    def list_accounts(self) -> dict:
        r = self.handle_request(
            method='GET',
            endpoint=f'/v4/{self.resource_name}',
            authenticated=True,
            timeout=2.5
        )
        return r.json()

    def list_balances(self, account: str) -> dict:
        r = self.handle_request(
            method='GET',
            endpoint=f'/v4/{self.resource_name}/{account}/balances',
            authenticated=True,
            timeout=2.5
        )
        return r.json()