# coding: utf-8
from commons.database import Database
import uuid


class Regex(object):
    def __init__(self, regex, type, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.regex = regex
        self.type = type

    greek_translator = {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd',
                             'e': '[e|ε]', 'f': 'f', 'g': 'g', 'h': 'h',
                             'i': '[i|ι|l]', 'j': 'j', 'k': 'k', 'l': '[i|ι|l]',
                             'm': 'm', 'n': '[n|ν]', 'o': '[o|ο]', 'p': '[p|ρ]',
                             'q': 'q', 'r': 'r', 's': 's', 't': 't',
                             'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x',
                             'y': '[y|υ]', 'z': 'z', "*": ".*"}

    def json(self):
        return {"regex": self.regex,
                "type": self.type,
                "_id": self._id}

    def add_entry(self):
        database = Database()
        database.initialize()
        database.insert("regex", self.json())

    @classmethod
    def get_main_regex(cls):
        database = Database()
        database.initialize()
        entry = database.find_one("regex", {"type": "main"})
        if entry is not None:
            return cls(**entry)
        else:
            bad_regex = Regex(regex='$^', type="main")
            return bad_regex

    @classmethod
    def update_main_regex(cls):
        old_main = cls.get_main_regex()
        new_main = cls.build_main_regex()
        new_main._id = old_main._id
        if old_main.regex != '$^':
            database = Database()
            database.initialize()
            database.update("regex", query=old_main.json(), update=new_main.json())
        else:
            new_main.add_entry()

    @classmethod
    def get_sub_entries(cls):
        database = Database()
        database.initialize()
        entries = database.find("regex", {"type":"sub"})
        return [cls(**entry) for entry in entries]

    @classmethod
    def build_main_regex(cls):
        samples = cls.get_sub_entries()
        regexs = "("
        sample_len = len(samples)
        count = 1
        for sample in samples:
            start = ""
            letters = []
            for letter in sample.regex:
                start += "{}"
                try:
                    let_regex = cls.greek_translator[letter]
                    letters.append(let_regex)
                except KeyError:
                    letters.append(letter)
            regex = start.format(*letters)
            if count != sample_len:
                regexs += regex + "|"
            else:
                regexs += regex + ")"
            count += 1
        main_regex = Regex(regex=regexs, type="main")
        return main_regex


regex = Regex(regex="newerreegx", type="sub")
regex.add_entry()
Regex.update_main_regex()
print(Regex.get_main_regex().regex)