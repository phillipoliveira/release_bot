# coding: utf-8
from commons.database import Database
import uuid
import unicodedata
import jellyfish
import itertools
from unidecode import unidecode


class Samples(object):
    def __init__(self, text, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.text = text

    def json(self):
        return {"text": self.text,
                "_id": self._id}

    def add_entry(self):
        database = Database()
        database.initialize()
        database.insert("samples", self.json())

    @classmethod
    def get_entries(cls):
        database = Database()
        database.initialize()
        entries = database.find("samples", ({}))
        return [cls(**entry) for entry in entries]

    @staticmethod
    def find_entry(text):
        database = Database()
        database.initialize()
        entry = database.find_one("samples", {"text": text})
        return entry

    @classmethod
    def evaluate(cls, msg):
        samples = cls.get_entries()
        nums = []
        no_weirdness = unidecode(msg)
        msg = unicodedata.normalize('NFKC', no_weirdness.lower().replace("\n", " "))
        for sample in samples:
            test_length = min(len(sample.text.split()), len(msg.split()))
            combinations = itertools.combinations(msg.split(), test_length)
            for combination in combinations:
                nums.append(jellyfish.jaro_distance(sample.text,
                                                    " ".join(combination)))
        if max(nums) > 0.85:
            return True
        else:
            return False

    @classmethod
    def test(cls):
        raws = ['DΕΡLΟΥΙΝG rel_70 to staging',
                "Deploying the latest rel_71 to staging",
                "rel_70\nRelease notes",
                "Deploying rel_70 to prod",
                "ＤＥＰＬＯＹＩＮＧ rel_71 to staging"]
        tests = []
        for i in raws:
            tests.append(Samples.evaluate(i))
        if all(tests):
            print("Tests passed")


Samples.test()

