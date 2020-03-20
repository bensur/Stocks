import lib.helpers as helpers
from management.DBManager import DBManager
import json
import re
from alpha_vantage.timeseries import TimeSeries


class StocksManager:
    def __init__(self):
        self.logger = helpers.get_logger()
        self.supported_paths = {
            "GET": ['account_summary', 'help'],
            "POST": ['register', 'buy', 'sell']
        }
        self.paths_help_message = {
            "account_summary": "GET Method. Returns the account summary. No query params needed.",
            "register": "POST Method. Register new user and return the generated token. POST body must contain username"
                        " and initial deposit",
            "buy": "POST Method. Buys stocks. "
                   "POST body must contain 'stocks' hash where the key is the name of stock and"
                   " the value is the number of stocks to buy",
            "sell": "POST Method. Sells stocks. "
                    "POST body must contain 'stocks' hash where the key is the name of stock to sell and"
                   " the value is the number of stocks to sell",
            "help": "Return this help summary"
        }
        for http_method in self.supported_paths.keys():
            for path in self.supported_paths[http_method]:
                if path not in self.paths_help_message:
                    self.logger.warn("Could not find help message for path '%s'" % path)
        self.requests_counter = 0
        self.DBM = DBManager()
        self.ts = TimeSeries(key="TEFK1KZP8TU5E11J")  # TODO: Fix hardcoded key

    def handle(self, path, headers, command, post_data=None):
        self.requests_counter += 1
        if post_data:
            post_data = json.loads(post_data.decode("utf-8"))
        self.logger.debug(str("request #%i: " % self.requests_counter) + json.dumps({"path": path,
                                                                                     "headers": dict(headers),
                                                                                     "command": command,
                                                                                     "post_data": post_data}))
        if command in self.supported_paths and path and \
           path.split("/")[1].split("?")[0] not in self.supported_paths[command]:
            return {"response": json.dumps({"response_message": "Error! path '" +
                                                                str(path.split("/")[1].split("?")[0]) +
                                                                "' is not supported for '" +
                                                                str(command) + "'"}),
                    "response_code": 400}
        if command == "POST":
            if re.match(r'^/register', path):
                return self.register(headers, post_data)
            elif re.match(r'^/buy', path):
                return self.update(headers, post_data, 'add')
            elif re.match(r'^/sell', path):
                return self.update(headers, post_data, 'sub')
            else:
                return {"response": json.dumps({"response_message": "Error! command '%s' not supported!" % command}),
                        "response_code": 400}
        elif command == "GET":
            query_params = self.get_query_params(path)
            if re.match(r'^/account_summary', path):
                return self.get_account_summary(headers, query_params)
            elif re.match(r'^/help', path):
                help_message = self.get_help_message()
                return {"response": json.dumps({"response_message": help_message}),
                        "response_code": 200}
            else:
                return {"response": json.dumps({"response_message": "Error! command '%s' not supported!" % command}),
                        "response_code": 400}
        else:
            return {"response": json.dumps({"response_message": "Error! command '%s' not supported!" % command}),
                    "response_code": 400}

    def get_help_message(self):
        docs_url = "https://docs.yourfriendlystocksexchange.com"
        help_message = "Welcome to your friendly stocks exchange!\n" \
                       "In order to use the service you need to use the register API (explained later on). " \
                       "The register API return a toket you must use in all future API request in " \
                       "HTTP header called 'token' (ie ['token': '<THE_TOKEN_RECEIVED>'.\n We support the following APIs:\n"
        for path in self.paths_help_message.keys():
            help_message += "\t%s - %s\n" % (path, self.paths_help_message[path])
        help_message += "\nYou can find the full documentation at %s" % docs_url
        return help_message

    @staticmethod
    def get_query_params(path):
        """
        Return dict
        :param path:
        :type path: str
        :return:
        :rtype: dict
        """
        if '?' in path:
            query_params = {}
            for pair in path.split("?")[1].split("&"):
                pair_l = pair.split("=")
                if len(pair_l) == 1:
                    query_params[pair_l[0]] = None
                elif len(pair_l) == 2:
                    query_params[pair_l[0]] = pair_l[1]
            return query_params
        else:
            return None

    def register(self, headers, post_data):
        self.logger.debug("Got register request")
        if 'username' not in post_data.keys():
            return {"response": json.dumps({"response_message": "username not sent in post body"}),
                    "response_code": 400}
        else:
            user = post_data["username"]
        if 'deposit' not in post_data.keys():
            return {"response": json.dumps({"response_message": "you must make initial deposit!"}),
                    "response_code": 400}
        else:
            deposit = post_data["deposit"]
        token = self.create_new_user(user, deposit)
        return {"response": json.dumps({"response_message": "Here is your token: %s" % token}),
                "response_code": 200}

    def update(self, headers, post_data, stocks_operation):
        user_id = self.validate_token(headers)
        if not post_data:
            self.logger.warn("No post data for request #%i" % self.requests_counter)
            return {"response": json.dumps({"response_message": "No post data for request"}),
                    "response_code": 400}
        if user_id:
            if 'stocks' not in post_data:
                self.logger.warn("User %s did not send stocks in the request" % user_id)
                self.logger.debug("Post data sent by user %s: %s" % (user_id, json.dumps(post_data)))
                return {"response": json.dumps({"response_message": "Request data does not contain 'stocks'!"}),
                        "response_code": 400}
            stocks = post_data["stocks"]
            self.logger.debug("User %s requested to buy %s" % (user_id, json.dumps(stocks)))
            balance = self.validate_balance(user_id, stocks, stocks_operation)
            if not balance:
                response_message = "User %s does not have enough in his balance to buy stocks %s" % (user_id,
                                                                                                     json.dumps(stocks))
                self.logger.warn(response_message)
                return {"response": json.dumps({"response_message": response_message}),
                        "response_code": 400}
            self.DBM.update(user_id, balance, stocks, stocks_operation)
            return {"response": json.dumps({"response_message": "Updated stocks!"}),
                    "response_code": 200}
        else:
            self.logger.warn("No valid token in request #%i" % self.requests_counter)
            return {"response": json.dumps({"response_message": "No valid token received"}),
                    "response_code": 401}

    def get_account_summary(self, headers, query_params):
        user_id = self.validate_token(headers)
        if user_id:
            self.logger.debug("Got account_summary request for user %s" % user_id)
            user = self.DBM.find(user_id)
            del user["_id"]
            del user["token"]
            return {"response": json.dumps(user),
                    "response_code": 200}
        else:
            self.logger.warn("No valid token in request #%i" % self.requests_counter)
            return {"response": json.dumps({"response_message": "No valid token received"}),
                    "response_code": 401}

    def validate_token(self, headers):
        if 'token' not in headers.keys():
            return False
        else:
            return self.DBM.is_user_exist(headers['token'])

    def create_new_user(self, username, deposit):
        action_status = self.DBM.insert(username, deposit)
        self.logger.debug("Create action status %s" % action_status)
        user = self.DBM.find(username)
        user["_id"] = str(user["_id"])
        self.logger.debug("Created new user %s" % json.dumps(user))
        return user["token"]

    def validate_balance(self, user_id, stocks, stocks_operation):
        total = 0
        for stock in stocks:
            total += self.get_stock_price(stock["name"]) * stock["amount"]
        user = self.DBM.find(user_id)
        cur_balance = user["balance"]
        if stocks_operation == "add":
            if cur_balance > total:
                return cur_balance - total
            else:
                return None
        elif stocks_operation == "sub":
            return cur_balance + total
        else:
            self.logger.error("stocks_operation '%s' is not supported in validate_balance function")

    def get_stock_price(self, stock_name):
        data, meta_data = self.ts.get_intraday(stock_name)  # TODO: check the stock exist?
        self.logger.debug("data: %s, metadata: %s" % (data, meta_data))
        stock_price = float(data[meta_data['3. Last Refreshed']]['4. close'])
        self.logger.debug("Price for %s is %f" % (stock_name, stock_price))
        return stock_price
