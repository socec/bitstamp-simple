import hashlib
import hmac
import time
import urllib.request


class HttpApi:
    """
    Bitstamp HTTP API available at: https://www.bitstamp.net/api/
    """
    def __init__(self):
        self._url_base = 'https://www.bitstamp.net/api'
        self._nonce = 0
        self._auth_params = ''

    def _get_nonce(self) -> int:
        # return greater value between incremented current nonce and current timestamp
        nonce = int(self._nonce + 1)
        timestamp = int(time.time())
        return max(nonce, timestamp)

    def _get_authentication_params(self, api_key: str, api_secret: str, client_id: str) -> bytes:
        # construct part of the request with authentication data
        api_secret = api_secret.encode('utf-8')
        nonce = str(self._get_nonce())
        message = (nonce + client_id + api_key).encode('utf-8')
        signature = hmac.new(api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
        data = 'key=%s&signature=%s&nonce=%s' % (api_key, str(signature), nonce)
        return data.encode('utf-8')

    @staticmethod
    def _http_request(url, data) -> bytes:
        if type(data) == str:
            data = data.encode('utf-8')
        with urllib.request.urlopen(url, data) as response:
            return response.read()

    def set_authentication_parameters(self, api_key: str, api_secret: str, client_id: str):
        self._auth_params = self._get_authentication_params(api_key, api_secret, client_id)

    def has_authentication_parameters(self):
        return not self._auth_params == ''

    # Public API

    def ticker(self):
        url = self._url_base + '/ticker'
        data = None
        return self._http_request(url, data)

    def ticker_hour(self):
        url = self._url_base + '/ticker_hour'
        data = None
        return self._http_request(url, data)

    def order_book(self):
        url = self._url_base + '/order_book'
        data = None
        return self._http_request(url, data)

    def transactions(self, time_scope: str='minute'):
        # time = minute, hour, day
        url = self._url_base + '/transactions?time=%s' % time_scope
        data = None
        return self._http_request(url, data)

    # Private API

    def balance(self):
        url = self._url_base + '/balance'
        data = self._auth_params
        return self._http_request(url, data)

    def user_transactions(self, offset: int=0, limit: int=200, sort: str='desc'):
        # sort = desc, asc
        url = self._url_base + '/user_transactions'
        data = '%s&offset=%s&limit=%s&sort=%s' % (self._auth_params, str(offset), str(limit), sort)
        return self._http_request(url, data)

    def open_orders(self):
        url = self._url_base + '/open_orders'
        data = self._auth_params
        return self._http_request(url, data)

    def order_status(self, order_id: int):
        url = self._url_base + '/order_status'
        data = self._auth_params + '&id=' + str(order_id)
        return self._http_request(url, data)

    def cancel_order(self, order_id: int):
        url = self._url_base + '/cancel_order'
        data = self._auth_params + '&id=' + str(order_id)
        return self._http_request(url, data)

    def cancel_all_orders(self):
        url = self._url_base + '/cancel_all_orders'
        data = self._auth_params
        return self._http_request(url, data)

    def buy(self, amount: float, price: float):
        url = self._url_base + '/buy'
        data = self._auth_params + '&amount=' + ('%.8f' % amount) + '&price=' + str(price)
        return self._http_request(url, data)

    def sell(self, amount: float, price: float):
        url = self._url_base + '/sell'
        data = self._auth_params + '&amount=' + ('%.8f' % amount) + '&price=' + str(price)
        return self._http_request(url, data)
