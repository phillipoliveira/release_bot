from commons.database import Database
import requests
import json
import random


class GiphyCommands(object):

    @staticmethod
    def get_token_from_database():
        database = Database()
        database.initialize()
        result = database.find_one("giphy_tokens", query=({}))
        return result['giphy_token']

    @staticmethod
    def get_keyword_from_database():
        database = Database()
        database.initialize()
        result = database.find_one("giphy_keyword", query=({}))
        return result['giphy_keyword']

    @classmethod
    def get_gif(cls):
        import requests
        data = (requests.get(
            "http://api.giphy.com/v1/gifs/search?q={}&api_key={}&limit=100".format(
                cls.get_keyword_from_database(),
                cls.get_token_from_database()
            )))
        return data.json()['data'][random.randint(0, 100)]['images']['original']['url']
