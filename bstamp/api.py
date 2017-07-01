# Bitstamp HTTP API functions
# https://www.bitstamp.net/api/
# =============================

import hashlib
import hmac
import time
import urllib.request


# API authentication functions
# ============================

def nonce_update(nonce: int):
    # return greater value between incremented nonce and current timestamp
    return int(max(int(nonce) + 1, int(time.time())))


def authentication(api_key: str, api_secret: str, client_id: str, nonce: int):
    api_secret = api_secret.encode('utf-8')
    nonce = str(nonce)
    message = (nonce + client_id + api_key).encode('utf-8')
    signature = hmac.new(api_secret, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
    ksn = 'key=%s&signature=%s&nonce=%s' % (str(api_key), str(signature), nonce)
    return ksn.encode('utf-8')


# API functions
# =============

base_url = 'https://www.bitstamp.net/api'


def _http_communication(url, data):
    if type(data) == str:
        data = data.encode('utf-8')
    with urllib.request.urlopen(url, data) as response:
        return response.read()


def ticker():
    # Returns JSON dictionary:
    # last - last BTC price
    # high - last 24 hours price high
    # low - last 24 hours price low
    # vwap - last 24 hours volume weighted average price: vwap
    # volume - last 24 hours volume
    # bid - highest buy order
    # ask - lowest sell order
    # timestamp - unix timestamp date and time
    url = base_url + '/ticker/'
    data = []
    return _http_communication(url, data)


def balance(authentication):
    # Params:
    # key - API key
    # signature - signature
    # nonce - nonce

    # Returns JSON dictionary:
    # usd_balance - USD balance
    # btc_balance - BTC balance
    # usd_reserved - USD reserved in open orders
    # btc_reserved - BTC reserved in open orders
    # usd_available- USD available for trading
    # btc_available - BTC available for trading
    # fee - customer trading fee

    url = base_url + '/balance/'
    data = authentication
    return _http_communication(url, data)


def user_transactions(authentication, offset=0, limit=200, sort='desc'):
    # Params:
    # key - API key
    # signature - signature
    # nonce - nonce
    # offset - skip that many transactions before beginning to return results. Default: 0.
    # limit - limit result to that many transactions. Default: 100.
    # sort - sorting by date and time (asc - ascending; desc - descending). Default: desc.

    # Returns descending JSON list of transactions. Every transaction (dictionary) contains:
    # datetime - date and time
    # id - transaction id
    # type - transaction type (0 - deposit; 1 - withdrawal; 2 - market trade)
    # usd - USD amount
    # btc - BTC amount
    # fee - transaction fee
    # order_id - executed order id

    url = base_url + '/user_transactions/'
    data = authentication + '&offset=' + str(offset) + '&limit=' + str(limit) + '&sort=' + sort
    return _http_communication(url, data)


def open_orders(authentication):
    # Params:
    # key - API key
    # signature - signature
    # nonce - nonce

    # Returns JSON list of open orders. Each order is represented as dictionary:
    # id - order id
    # datetime - date and time
    # type - buy or sell (0 - buy; 1 - sell)
    # price - price
    # amount - amount

    url = base_url + '/open_orders/'
    data = authentication
    return _http_communication(url, data)


def cancel_order(authentication, order_id):
    # Params:
    # key - API key
    # signature - signature
    # nonce - nonce
    # id - order ID

    # Returns 'true' if order has been found and canceled.

    url = base_url + '/cancel_order/'
    data = authentication + '&id=' + str(order_id)
    return _http_communication(url, data)


def buy(authentication, amount, price):
    # Params:
    # key - API key
    # signature - signature
    # nonce - nonce
    # amount - amount
    # price - price

    # Returns JSON dictionary representing order:
    # id - order id
    # datetime - date and time
    # type - buy or sell (0 - buy; 1 - sell)
    # price - price
    # amount - amount

    url = base_url + '/buy/'
    data = authentication + '&amount=' + ('%.8f' % amount) + '&price=' + str(price)
    return _http_communication(url, data)


def sell(authentication, amount, price):
    # Params:
    # key - API key
    # signature - signature
    # nonce - nonce
    # amount - amount
    # price - price

    # Returns JSON dictionary representing order:
    # id - order id
    # datetime - date and time
    # type - buy or sell (0 - buy; 1 - sell)
    # price - price
    # amount - amount

    url = base_url + '/sell/'
    data = authentication + '&amount=' + ('%.8f' % amount) + '&price=' + str(price)
    return _http_communication(url, data)
