import cmd, json, getopt
import api, authorization

# Command interpreter for Bitstamp API
class BitstampCmd(cmd.Cmd):

	# session data
	# ============

	nonce = 0
	api_key = "xxx"
	api_secret = "xxx"
	client_id = "xxx"

	# overriding interpreter setup
	# ============================

	prompt = "bstamp$ "

	def emptyline(self):
		return

	def default(self, args):
		print "*** unknown command ***"
		self.do_help(None)

	def preloop(self):
		ret = raw_input("Load authorization data? [y/n]: ")
		if (ret == "y"):
			auth_data = authorization.load()
			if (auth_data != []):
				self.api_key, self.api_secret, self.client_id = auth_data
		return

	def postloop(self):
		self.api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.api_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
		self.client_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

	def precmd(self, args):
		arglist = self._args_to_list(args)
		if (len(arglist) != 0) and (arglist[0] == "authorization"):
			return args
		if (self.api_key == "xxx") or (self.api_secret == "xxx") or (self.client_id == "xxx"):
			print "No authorization data, please run authorization command."
		return args

	# private functions
	# =================

	# prepare API authorization
	def _api_auth(self):
		self.nonce = api.nonce_update(self.nonce)
		return api.authorization(self.api_key, self.api_secret, self.client_id, self.nonce)

	# convert a string with arguments to a list with arguments
	def _args_to_list(self, args):
		if (len(args) == 0):
			return []
		else:
			return args.split()

	# check if share range is invalid
	def _share_invalid(self, share):
		if (float(share) < 0.0) or (float(share) > 1.0):
			print "Requested share {} is not in valid range [0.0 - 1.0].".format(share)
			return True
		else:
			return False

	# commands
	# ========

	# enter authorization data
	def help_authorization(self):
		print "\nUSAGE:"
		print "\tauthorization [--load] [--save] [key secret id]"
		print "DESCRIPTION:"
		print "\tManage API key, API secret and client ID for private API calls.\n"
		print "\t[key secret id]  Enter authorization data for current session."
		print "\t[--save]         Saves current authorization data to a local file."
		print "\t[--load]         Loads authorization data from a local file."
	def do_authorization(self, args):
		try:
			opts, args = getopt.getopt(args.split(), '', ['save', 'load'])
		except getopt.GetoptError as err:
			print str(err)
			opts, args = ([], [])
		if (len(args) > 3 or (len(args) < 3 and len(opts) != 1)):
			self.do_help("authorization")
			return
		if (len(args) == 3): 
			self.api_key, self.api_secret, self.client_id = args
		if (len(opts) == 1):
			if ('--save' == opts[0][0]):
				authorization.save(self.api_key, self.api_secret, self.client_id)
				print "Authorization data saved."
			if ('--load' == opts[0][0]):
				auth_data = authorization.load()
				if (auth_data != []):
					self.api_key, self.api_secret, self.client_id = auth_data
					print "Authorization data loaded."

	# show balance
	def help_balance(self):
		print "\nUSAGE:"
		print "\tbalance"
		print "DESCRIPTION:"
		print "\tShow current account balance."
	def do_balance(self, args):
		auth = self._api_auth()
		ret = json.loads(api.balance(auth))
		print json.dumps(ret, indent=2)

	# buy BTC
	def help_buy(self):
		print "\nUSAGE:"
		print "\tbuy [-s usd_share] | [-a usd_amount] <price>"
		print "DESCRIPTION:"
		print "\tBuy BTC at requested price by spending available USD.\n"
		print "\t[-s usd_share]   Specify share of available USD to spend (e.g. 0.314)."
		print "\t[-a usd_amount]  Specify amount of available USD to spend (e.g. 31.4)."
	def do_buy(self, args):
		try:
			opts, args = getopt.getopt(args.split(), 's:a:')
		except getopt.GetoptError as err:
			print str(err)
			opts, args = ([], [])
		if (len(opts) != 1 or len(args) != 1):
			self.do_help("buy")
			return
		price = args[0]
		auth = self._api_auth()
		usd_available = json.loads(api.balance(auth))["usd_available"]
		btc_amount = 0.0
		if ('-s' == opts[0][0]):
			usd_share = opts[0][1]
			if (float(usd_share) < 0.0 or float(usd_share) > 1.0):
				print "USD share {} not in expected range (0.0 - 1.0).".format(usd_share)
				return
			btc_amount = (float(usd_share) * float(usd_available)) / float(price)
		if ('-a' == opts[0][0]):
			usd_amount = opts[0][1]
			if (float(usd_amount) < 0.0 or float(usd_amount) > float(usd_available)):
				print "USD amount {} not available.".format(usd_amount)
				return
			btc_amount = float(usd_amount) / float(price)
		if (btc_amount == 0.0):
			print "Can't buy 0.0 BTC."
			return
		confirm = raw_input("Buying {} BTC for {} USD/BTC? [y/n]: ".format(btc_amount, price))
		if (confirm != "y"):
			return
		auth = self._api_auth()
		print api.buy(auth, btc_amount, price)

	# sell BTC
	def help_sell(self):
		print "\nUSAGE:"
		print "\tsell [-s btc_share] | [-a btc_amount] <price>"
		print "DESCRIPTION:"
		print "\tSell available BTC at requested price.\n"
		print "\t[-s btc_share]   Specify share of available BTC to sell (e.g. 0.314)."
		print "\t[-a btc_amount]  Specify amount of available BTC to sell (e.g. 3.14)."
	def do_sell(self, args):
		try:
			opts, args = getopt.getopt(args.split(), 's:a:')
		except getopt.GetoptError as err:
			print str(err)
			opts, args = ([], [])
		if (len(opts) != 1 or len(args) != 1):
			self.do_help("sell")
			return
		price = args[0]
		auth = self._api_auth()
		btc_available = json.loads(api.balance(auth))["btc_available"]
		btc_amount = 0.0
		if ('-s' == opts[0][0]):
			btc_share = opts[0][1]
			if (float(btc_share) < 0.0 or float(btc_share) > 1.0):
				print "BTC share {} not in expected range (0.0 - 1.0).".format(btc_share)
				return
			btc_amount = float(btc_share) * float(btc_available)
		if ('-a' == opts[0][0]):
			btc_amount = opts[0][1]
			if (float(btc_amount) < 0.0 or float(btc_amount) > float(btc_available)):
				print "BTC amount {} not available.".format(btc_amount)
				return
		if (btc_amount == 0.0):
			print "Can't sell 0.0 BTC."
			return
		confirm = raw_input("Selling {} BTC for {} USD/BTC? [y/n]: ".format(btc_amount, price))
		if (confirm != "y"):
			return
		auth = self._api_auth()
		print api.sell(auth, btc_amount, price)

	# show orders
	def help_orders(self):
		print "\nUSAGE:"
		print "\torders"
		print "DESCRIPTION:"
		print "\tShow currently open orders."
	def do_orders(self, args):
		auth = self._api_auth()
		ret = json.loads(api.open_orders(auth))
		for item in ret:
			print json.dumps(item)

	# cancel order
	def help_cancel(self):
		print "\nUSAGE:"
		print "\tcancel <order_id>"
		print "DESCRIPTION:"
		print "\tCancel an open order."
	def do_cancel(self, args):
		try:
			opts, args = getopt.getopt(args.split(), '')
		except getopt.GetoptError as err:
			print str(err)
			opts, args = ([], [])
		if (len(args) != 1):
			self.do_help("cancel")
			return
		order_id = args[0]
		auth = self._api_auth()
		print api.cancel_order(auth, order_id)

	# show transactions
	def help_transactions(self):
		print "\nUSAGE:"
		print "\ttransactions [num_last]"
		print "DESCRIPTION:"
		print "\tShow list of transactions in descending order.\n"
		print "\t[num_last]  Show only that many last transactions."
	def do_transactions(self, args):
		try:
			opts, args = getopt.getopt(args.split(), '')
		except getopt.GetoptError as err:
			print str(err)
			opts, args = ([], [])
		if (len(args) > 1):
			self.do_help("transactions")
			return
		auth = self._api_auth()
		if (len(args) == 1):
			limit = args[0]
			ret = json.loads(api.user_transactions(auth, limit=limit))
		else:
			ret = json.loads(api.user_transactions(auth))
		for item in ret:
			print json.dumps(item)

	# exit
	def help_exit(self):
		print "\nUSAGE:"
		print "\texit"
		print "DESCRIPTION:"
		print "\tExit the program."
	def do_exit(self, args):
		return True

# execute if module is run directly (not imported)
if __name__ == "__main__":
	BitstampCmd().cmdloop()
