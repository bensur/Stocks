import lib.helpers as helpers


class StocksManager:
    def __init__(self):
        self.logger = helpers.get_logger()
        self.supported_paths = {
            "GET": ['account_summary'],
            "POST": ['register', 'buy', 'sell']
        }

    def handle(self, path, headers, command, post_data=None):
        self.logger.debug('path=' + str(path))
        self.logger.debug('path.split("/")[1]=' + path.split("/")[1].split("?")[0])
        if command in self.supported_paths and path and path.split("/")[1].split("?")[0] not in self.supported_paths[command]:
            return {"response": "Error! path '" + str(path.split("/")[1].split("?")[0]) + "' is not supported for '" + str(command) + "'",
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
        return {"response": "Here is your user",
                "response_code": 200}

    def buy(self, headers, post_data):
        self.logger.debug("Got buy request")
        return {"response": "Bought!",
                "response_code": 200}

    def sell(self, headers, post_data):
        self.logger.debug("Got sell request")
        return {"response": "Sold!",
                "response_code": 200}

    def get_account_summary(self, headers, query_params):
        self.logger.debug("Got account_summary request")
        return {"response": "Who are you?",
                "response_code": 200}
