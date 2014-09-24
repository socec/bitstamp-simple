import cmd, json
import api_bitstamp as bs
import authorization

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
		self.nonce = bs.update_nonce(self.nonce)
		return bs.get_authorization(self.api_key, self.api_secret, self.client_id, self.nonce)

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
		print "USAGE:"
		print "\t authorization <api_key> <api_secret> <client_id> [-s]"
		print "DESCRIPTION:"
		print "\t Enter API key, API secret and client ID for authorization of private API calls."
		print "\t Providing \"-s\" option stores them (plaintext) to a file in the current directory."
	def do_authorization(self, args):
		arglist = self._args_to_list(args)
		if ((len(arglist) < 3) or (len(arglist) > 4)):
			self.do_help("authorization")
			return
		self.api_key = arglist[0]
		self.api_secret = arglist[1]
		self.client_id = arglist[2]
		if ((len(arglist) == 4) and (arglist[3] == "-s")):
			authorization.save(self.api_key, self.api_secret, self.client_id)

	# show balance
	def help_balance(self):
		print "USAGE:"
		print "\t balance"
		print "DESCRIPTION:"
		print "\t Show current account balance."
	def do_balance(self, args):
		auth = self._api_auth()
		ret = json.loads(bs.api_balance(auth))
		print json.dumps(ret, indent=2)

	# buy BTC
	def help_buy(self):
		print "USAGE:"
		print "\t buy <usd_share> <price>"
		print "DESCRIPTION:"
		print "\t Buy BTC at requested price by spending requested share [0.0, 1.0] of available USD."
		print "\t e.g. buy 0.25 100.0"
	def do_buy(self, args):
		arglist = self._args_to_list(args)
		if (len(arglist) != 2):
			self.do_help("buy")
			return
		usd_share, price = arglist
		if (self._share_invalid(usd_share)):
			return
		auth = self._api_auth()
		usd_available = json.loads(bs.api_balance(auth))["usd_available"]
		btc_amount = (float(usd_share) * float(usd_available)) / float(price)
		if (btc_amount == 0.0):
			print "BTC amount is 0"
			return
		print "buying {} BTC for {} USD/BTC".format(btc_amount, price)
		auth = self._api_auth()
		print bs.api_buy(auth, btc_amount, price)

	# sell BTC
	def help_sell(self):
		print "USAGE:"
		print "\t sell <btc_share> <price>"
		print "DESCRIPTION:"
		print "\t Sell requested share [0.0, 1.0] of available BTC at requested price."
		print "\t e.g. sell 0.25 100.0"
	def do_sell(self, args):
		arglist = self._args_to_list(args)
		if (len(arglist) != 2):
			self.do_help("sell")
			return
		btc_share, price = arglist
		if (self._share_invalid(btc_share)):
			return
		auth = self._api_auth()
		btc_available = json.loads(bs.api_balance(auth))["btc_available"]
		btc_amount = float(btc_share) * float(btc_available)
		if (btc_amount == 0.0):
			print "BTC amount is 0"
			return
		print "selling {} BTC for {} USD/BTC".format(btc_amount, price)
		auth = self._api_auth()
		print bs.api_sell(auth, btc_amount, price)

	# show orders
	def help_orders(self):
		print "USAGE:"
		print "\t orders"
		print "DESCRIPTION:"
		print "\t Show currently open orders."
	def do_orders(self, args):
		auth = self._api_auth()
		ret = json.loads(bs.api_open_orders(auth))
		for item in ret:
			print json.dumps(item)

	# cancel order
	def help_cancel(self):
		print "USAGE:"
		print "\t cancel <order_id>"
		print "DESCRIPTION:"
		print "\t Cancel an open order."
	def do_cancel(self, args):
		arglist = self._args_to_list(args)
		if (len(arglist) != 1):
			self.do_help("cancel")
			return
		order_id = arglist[0]
		auth = self._api_auth()
		print bs.api_cancel_order(auth, order_id)

	# show transactions
	def help_transactions(self):
		print "USAGE:"
		print "\t transactions [num_last]"
		print "DESCRIPTION:"
		print "\t Show list of transactions in descending order."
		print "\t Providing [num_last] parameter will show only that many last transactions."
	def do_transactions(self, args):
		arglist = self._args_to_list(args)
		if (len(arglist) > 1):
			self.do_help("transactions")
			return
		auth = self._api_auth()
		if (len(arglist) == 1):
			limit = arglist[0]
			ret = json.loads(bs.api_user_transactions(auth, limit=limit))
		else:
			ret = json.loads(bs.api_user_transactions(auth))
		for item in ret:
			print json.dumps(item)

	# exit
	def help_exit(self):
		print "USAGE:"
		print "\t exit"
		print "DESCRIPTION:"
		print "\t Exit the program."
	def do_exit(self, args):
		return True

# execute if module is run directly (not imported)
if __name__ == "__main__":
	BitstampCmd().cmdloop()
