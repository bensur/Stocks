import lib.helpers as helpers
from pymongo import MongoClient
import uuid
import json
import sys


class DBManager:
    def __init__(self):
        self.logger = helpers.get_logger()
        try:
            self.client = MongoClient('localhost', 27017)
        except Exception as e:
            self.logger.fatal("Could not open connection to mongodb!")
            self.logger.debug(e)
            sys.exit(1)
        self.db = self.client["stocks"]
        self.stocks_col = self.db["stocks"]
        self.stocks_col.create_index("user_id", unique=True)

    def is_user_exist(self, token):
        query = {"token": token}
        result = self.stocks_col.find_one(query)
        return result["user_id"]

    def insert(self, user_id, deposit):
        user_data = {"user_id": user_id,
                     "balance": deposit,
                     "stocks": [],
                     "token": str(uuid.uuid4())}
        self.logger.debug("Created new user: %s" % json.dumps(user_data))
        action_status = self.stocks_col.insert_one(user_data)
        return action_status

    def update(self, user_id, balance, stocks, operation):
        new_stocks = self.assemble_stocks(user_id, stocks, operation)
        query = {"user_id": user_id}
        value = {"$set": {"balance": balance, "stocks": new_stocks}}
        self.logger.debug("Updating user %s with %s" % (user_id, json.dumps(value)))
        return self.stocks_col.update_one(query, value)

    def find(self, user_id):
        query = {"user_id": user_id}
        result = self.stocks_col.find_one(query)
        return result

    def assemble_stocks(self, user_id, new_stocks, operation):
        if operation not in ['add', 'sub']:
            raise Exception("Operation %s is not supported" % operation)
        user_data = self.find(user_id)
        cur_stocks = user_data["stocks"]
        if not cur_stocks or len(cur_stocks) == 0:
            return new_stocks
        else:
            updated_stocks = {}
            for stock_name in new_stocks.keys():
                if stock_name in cur_stocks.keys():
                    if operation == 'add':
                        updated_stocks[stock_name] = cur_stocks[stock_name] + new_stocks[stock_name]
                    elif operation == 'sub':
                        updated_stocks[stock_name] = cur_stocks[stock_name] - new_stocks[stock_name]
                else:
                    updated_stocks[stock_name] = new_stocks[stock_name]
            for stock_name in cur_stocks.keys():
                if stock_name not in updated_stocks.keys():
                    updated_stocks[stock_name] = cur_stocks[stock_name]
            return updated_stocks


'''
user schema:
UID -> serial?
token -> UUID
balance -> float
stocks -> dict/hash

'''