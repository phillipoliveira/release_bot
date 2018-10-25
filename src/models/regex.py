from src.commons.database import Database
import uuid



class MessageLog(object):
    def __init__(self, regex, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.regex = regex
        greek_translator = {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd',
                            'e': '[e|ε]', 'f': 'f', 'g': 'g', 'h': 'h',
                            'i': '[i|ι|l]', 'j': 'j', 'k': 'k', 'l': '[i|ι|l]',
                            'm': 'm', 'n': '[n|ν]', 'o': '[o|ο]', 'p': '[p|ρ]',
                            'q': 'q', 'r': 'r', 's': 's', 't': 't',
                            'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x',
                            'y': '[y|υ]', 'z': 'z', "*": ".*"}

    def json(self):
        return {"regex": self.regex,
                "_id": self._id}

    def add_entry(self):
        database = Database()
        database.initialize()
        database.insert("regex", self.json())

    def get_entries(self):
        database = Database()
        database.initialize()
        database.insert("regex", self.json())

    @classmethod
    def evaluate_message(cls, message):

    @classmethod
    def get_regex(cls):


