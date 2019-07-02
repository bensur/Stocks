import lib.helpers as helpers
from management.DBManager import DBManager
import json


class StocksManager:
    def __init__(self):
        self.logger = helpers.get_logger()
        self.supported_paths = {
            "GET": ['account_summary'],
            "POST": ['register', 'buy', 'sell']
        }
        self.requests_counter = 0
        self.DBM = DBManager()

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
            return {"response": "Error! path '" + str(path.split("/")[1].split("?")[0]) +
                    "' is not supported for '" + str(command) + "'",
                    "response_code": 400}
        if command == "POST":
            if "register" in path:
                return self.register(headers, post_data)
            elif "buy" in path:
                return self.buy(headers, post_data)
            elif "sell" in path:
                return self.sell(headers, post_data)
        elif command == "GET":
            query_params = self.get_query_params(path)
            if 'account_summary' in path:
                return self.get_account_summary(headers, query_params)
            pass
        else:
            return {"response": "Error! command '%s' not supported!" % command, "response_code": 400}

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
            return {"response": "username not sent in post body",
                    "response_code": 400}
        else:
            user = post_data["username"]
        if 'deposit' not in post_data.keys():
            return {"response": "you must make initial deposit!",
                    "response_code": 400}
        else:
            deposit = post_data["deposit"]
        token = self.create_new_user(user, deposit)
        return {"response": "Here is your token: %s" % token,
                "response_code": 200}

    def buy(self, headers, post_data):
        user_id = self.validate_token(headers)
        stocks = post_data["stocks"]
        self.logger.debug("User %s requested to buy %s" % (user_id, json.dumps(stocks)))
        if user_id:
            balance = self.validate_balance(user_id, stocks)
            if not balance:
                self.logger.warn("User %s does not have enough in his balance to buy stocks %s" % (user_id,
                                                                                                   json.dumps(stocks)))
                return {"response": "User %s does not have enough in his balance to buy stocks %s" % (user_id,
                                                                                                      json.dumps(stocks)),
                        "response_code": 400}
            self.DBM.update(user_id, balance, stocks)
            return {"response": "Bought!",
                    "response_code": 200}
        else:
            self.logger.warn("No valid token in request #%i" % self.requests_counter)
            return {"response": "No valid token received",
                    "response_code": 401}

    def sell(self, headers, post_data):
        user_id = self.validate_token(headers)
        if user_id:
            self.logger.debug("Got sell request")
            return {"response": "Sold!",
                    "response_code": 200}
        else:
            self.logger.warn("No valid token in request #%i" % self.requests_counter)
            return {"response": "No valid token received",
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
            return {"response": "No valid token received",
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

    def validate_balance(self, user_id, stocks):
        total = 0
        for stock in stocks:
            total += self.get_stock_price(stock["name"]) * stock["amount"]
        user = self.DBM.find(user_id)
        cur_balance = user["balance"]
        if cur_balance > total:
            return cur_balance - total
        else:
            return None

    def get_stock_price(self, stock_name):
        stock_price = 1
        self.logger.debug("Price for %s is %i" % (stock_name, stock_price))
        return stock_price
