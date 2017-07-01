import cmd
import getopt
import json

import bstamp.api as api
import bstamp.authentication as authentication


# Command interpreter for Bitstamp API
class BitstampCmd(cmd.Cmd):
    # session data
    # ============

    nonce = 0
    api_key = 'X'
    api_secret = 'X'
    client_id = 'X'

    # overriding interpreter setup
    # ============================

    prompt = 'bstamp$ '

    def emptyline(self):
        return

    def default(self, args):
        print('*** unknown command ***')
        self.do_help(None)

    def preloop(self):
        ret = raw_input('Load authentication data? [y/n]: ')
        if ret == 'y':
            self.do_authentication('--load')
        return

    def postloop(self):
        self.api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        self.api_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        self.client_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

    def precmd(self, args):
        if len(args) != 0:
            if (args.split()[0] != 'authentication') and self._auth_is_missing():
                print('No authentication data, please run authentication command.')
        return args

    # private functions
    # =================

    # prepare API authentication
    def _api_auth(self):
        self.nonce = api.nonce_update(self.nonce)
        return api.authentication(self.api_key, self.api_secret, self.client_id, self.nonce)

    # check if authentication data is missing
    def _auth_is_missing(self):
        return (self.api_key == 'X') or (self.api_secret == 'X') or (self.client_id == 'X')

    # commands
    # ========

    # show ticker info
    def help_ticker(self):
        print('\nDESCRIPTION:')
        print('    Show last price, highest bid and lowest ask.')
        print('USAGE:')
        print('    ticker')

    def do_ticker(self, args):
        ret = json.loads(api.ticker())
        print('bid {} | price {} | ask {}'.format(ret['bid'], ret['last'], ret['ask']))

    # enter authentication data
    def help_authentication(self):
        print('\nDESCRIPTION:')
        print('    Manage API key, API secret and client ID for private API calls.')
        print('USAGE:')
        print('    authentication [options]')
        print('        [key secret id]  Enter authentication data for current session')
        print('        [--save]         Save current authentication data to a local file')
        print('        [--load]         Load authentication data from a local file')

    def do_authentication(self, args):
        try:
            opts, args = getopt.getopt(args.split(), '', ['save', 'load'])
        except getopt.GetoptError as err:
            print(str(err))
            opts, args = ([], [])
        if len(args) > 3 or (len(args) < 3 and len(opts) != 1):
            self.do_help('authentication')
            return
        if len(args) == 3:
            self.api_key, self.api_secret, self.client_id = args
        if len(opts) == 1:
            if '--save' == opts[0][0]:
                authentication.save(self.api_key, self.api_secret, self.client_id)
                print('Authentication data saved.')
            if '--load' == opts[0][0]:
                auth_data = authentication.load()
                if auth_data:
                    self.api_key, self.api_secret, self.client_id = auth_data
                    print('Authentication data loaded for client ID: {}'.format(self.client_id))

    # show balance
    def help_balance(self):
        print('\nDESCRIPTION:')
        print('    Show current account balance.')
        print('USAGE:')
        print('    balance')

    def do_balance(self, args):
        ret = json.loads(api.balance(self._api_auth()))
        print(json.dumps(ret, indent=2))

    # buy BTC
    def help_buy(self):
        print('\nDESCRIPTION:')
        print('    Buy BTC at requested price by spending available USD.')
        print('USAGE:')
        print('    buy [options] <price>')
        print('        [-s usd_share]   Specify share of available USD to spend (e.g. 0.314)')
        print('        [-a usd_amount]  Specify amount of available USD to spend (e.g. 31.4)')

    def do_buy(self, args):
        try:
            opts, args = getopt.getopt(args.split(), 's:a:')
        except getopt.GetoptError as err:
            print(str(err))
            opts, args = ([], [])
        if (len(opts) != 1) or (len(args) != 1):
            self.do_help('buy')
            return
        price = float(args[0])
        usd_available = float(json.loads(api.balance(self._api_auth()))['usd_available'])
        # correct available USD for the fee
        balance_json = json.loads(api.balance(self._api_auth()))
        fee = (float(balance_json['fee']) / 100.0)
        usd_available = usd_available * (1.0 - fee) - 0.01
        print('Available USD for buying: ' + str(usd_available))
        btc_amount = 0.0
        if '-s' == opts[0][0]:
            usd_share = float(opts[0][1])
            if (usd_share < 0.0) or (usd_share > 1.0):
                print('USD share {} not in expected range (0.0 - 1.0).'.format(usd_share))
                return
            btc_amount = (usd_share * usd_available) / price
        if '-a' == opts[0][0]:
            usd_amount = float(opts[0][1])
            if (usd_amount < 0.0) or (usd_amount > usd_available):
                print('USD amount {} not available.'.format(usd_amount))
                return
            btc_amount = usd_amount / price
        if btc_amount == 0.0:
            print('Can\'t buy 0.0 BTC.')
            return
        confirm = raw_input('Buying {} BTC for {} USD/BTC? [y/n]: '.format(btc_amount, price))
        if confirm != 'y':
            return
        print(api.buy(self._api_auth(), btc_amount, price))

    # sell BTC
    def help_sell(self):
        print('\nDESCRIPTION:')
        print('    Sell available BTC at requested price.')
        print('USAGE:')
        print('    sell [options] <price>')
        print('        [-s btc_share]   Specify share of available BTC to sell (e.g. 0.314)')
        print('        [-a btc_amount]  Specify amount of available BTC to sell (e.g. 3.14)')

    def do_sell(self, args):
        try:
            opts, args = getopt.getopt(args.split(), 's:a:')
        except getopt.GetoptError as err:
            print(str(err))
            opts, args = ([], [])
        if (len(opts) != 1) or (len(args) != 1):
            self.do_help('sell')
            return
        price = float(args[0])
        btc_available = float(json.loads(api.balance(self._api_auth()))['btc_available'])
        btc_amount = 0.0
        if '-s' == opts[0][0]:
            btc_share = float(opts[0][1])
            if (btc_share < 0.0) or (btc_share > 1.0):
                print('BTC share {} not in expected range (0.0 - 1.0).'.format(btc_share))
                return
            btc_amount = btc_share * btc_available
        if '-a' == opts[0][0]:
            btc_amount = float(opts[0][1])
            if (btc_amount < 0.0) or (btc_amount > btc_available):
                print('BTC amount {} not available.'.format(btc_amount))
                return
        if btc_amount == 0.0:
            print('Can\'t sell 0.0 BTC.')
            return
        confirm = raw_input('Selling {} BTC for {} USD/BTC? [y/n]: '.format(btc_amount, price))
        if confirm != 'y':
            return
        print(api.sell(self._api_auth(), btc_amount, price))

    # show orders
    def help_orders(self):
        print('\nDESCRIPTION:')
        print('    Show currently open orders.')
        print('USAGE:')
        print('    orders')

    def do_orders(self, args):
        ret = json.loads(api.open_orders(self._api_auth()))
        for item in ret:
            print(json.dumps(item))

    # cancel order
    def help_cancel(self):
        print('\nDESCRIPTION:')
        print('    Cancel an open order.')
        print('USAGE:')
        print('    cancel <order_id>')

    def do_cancel(self, args):
        try:
            opts, args = getopt.getopt(args.split(), '')
        except getopt.GetoptError as err:
            print(str(err))
            opts, args = ([], [])
        if len(args) != 1:
            self.do_help('cancel')
            return
        order_id = args[0]
        print(api.cancel_order(self._api_auth(), order_id))

    # show transactions
    def help_transactions(self):
        print('\nDESCRIPTION:')
        print('    Show list of transactions in descending order.')
        print('USAGE:')
        print('    transactions [options]')
        print('        [num_last]  Show only that many last transactions')

    def do_transactions(self, args):
        try:
            opts, args = getopt.getopt(args.split(), '')
        except getopt.GetoptError as err:
            print(str(err))
            opts, args = ([], [])
        if len(args) > 1:
            self.do_help('transactions')
            return
        if len(args) == 1:
            limit = args[0]
            ret = json.loads(api.user_transactions(self._api_auth(), limit=limit))
        else:
            ret = json.loads(api.user_transactions(self._api_auth()))
        for item in ret:
            print(json.dumps(item))

    # exit
    def help_exit(self):
        print('\nDESCRIPTION:')
        print('    Exit the program.')
        print('USAGE:')
        print('    exit')

    def do_exit(self, args):
        return True


def execute():
    BitstampCmd().cmdloop()
