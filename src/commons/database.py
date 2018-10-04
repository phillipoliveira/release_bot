import pymongo


class Database(object):
    URI = "mongodb://127.0.0.1:27017"
    # URI = Universal Resource Identifier
    DATABASE = None

    @staticmethod
    # this decorator is used to denote  a static method
    # - i.e.; a method that doesn't use self attributes.
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['release_bot']

    @staticmethod
    def insert(collection,data):
        Database.DATABASE[collection].insert(data)

    # The find method will return the data object.
    # You'd then need to use list comprehension to
    # return individual lines of object
    @staticmethod
    def find(collection,query):
        return Database.DATABASE[collection].find(query)

    # The find_one method will return first JSON
    # object in the database, that corresponds with the 'query'.
    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update(collection, query, update):
        Database.DATABASE[collection].update(query, update)
        return

    @staticmethod
    def remove(collection, query):
        Database.DATABASE[collection].remove(query)
        return

    @staticmethod
    def delete_many(collection, query):
        Database.DATABASE[collection].delete_many(query)
        return
