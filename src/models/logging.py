from src.commons.database import Database


class Logging(object):

    @staticmethod
    def add_entry(data):
        database = Database()
        database.initialize()
        database.insert("logging", data)
