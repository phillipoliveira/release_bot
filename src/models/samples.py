# coding: utf-8
from commons.database import Database
import uuid
import unicodedata
import jellyfish
import itertools
from unidecode import unidecode
from jira import JIRA
import re
import time


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

    @classmethod
    def find_entry(cls, text):
        database = Database()
        database.initialize()
        entry = database.find_one("samples", {"text": text})
        if entry is not None:
            return cls(**entry)
        else:
            return None

    def remove_entry(self):
        database = Database()
        database.initialize()
        database.remove("samples", self.json())

    # @classmethod
    # def evaluate(cls, msg):
    #     samples = cls.get_entries()
    #     nums = []
    #     no_weirdness = unidecode(msg)
    #     # cast all characters to ascii
    #     if not re.search("\?", no_weirdness):
    #         msg = unicodedata.normalize('NFKC', no_weirdness.lower().replace("\n", " "))[:120]
    #         # normalize, only judge the first 120 characters
    #         len_set = set()
    #         combo_dict = {}
    #         for sample in samples:
    #             len_set.add(min(len(sample.text.split()), len(msg.split())))
    #         # make a list of the different combination lengths you'll need to check
    #         for l in len_set:
    #             combo_dict[l] = list(itertools.combinations(msg.split(), l))
    #         # bake that list into a dict, tying it together with all combinations of that length
    #         for sample in samples:
    #             test_length = min(len(sample.text.split()), len(msg.split()))
    #             combinations = combo_dict[test_length]
    #             for combination in combinations:
    #                 nums.append(jellyfish.jaro_distance(sample.text,
    #                                                     " ".join(combination)))
    #     else:
    #         return False
    #     if max(nums, default=0) > 0.85:
    #         return True
    #     else:
    #         return False
    #
    # @classmethod
    # def test(cls):
    #     samples = ["deploying rel_ to staging",
    #                "deployed rel_ to staging",
    #                "deployed rel_ to prod",
    #                "deploying rel_ to prod",
    #                "rel_ release notes"]
    #
    #     for sample in samples:
    #         sample = Samples(text=sample)
    #         sample.add_entry()
    #
    #     raws = ['DΕΡLΟΥΙΝG rel_70 to staging',
    #             "Deploying the latest rel_71 to staging",
    #             "rel_70\nRelease notes",
    #             "Deploying rel_70 to prod",
    #             "ＤＥＰＬＯＹＩＮＧ rel_71 to staging"]
    #     tests = []
    #     for i in raws:
    #         tests.append(Samples.evaluate(i))
    #     print("{}/5 tests passed".format(sum(tests)))
    #
    #     for sample in samples:
    #         sample_obj = Samples.find_entry(sample)
    #         sample_obj.remove_entry()


# Samples.test()

    @staticmethod
    def get_latest_release():
        database = Database()
        database.initialize()
        entries = database.find(collection="version_record",
                                query={})
        saved_entries = list()
        times = list()
        for i in entries:
            times.append(i['time'])
            saved_entries.append(i)
        max_time = max(times)
        for i in saved_entries:
            if i['time'] == max_time:
                version = i['version']
                return version

    @staticmethod
    def get_release_notes(version):
        database = Database()
        database.initialize()
        jira_settings = database.find_one("jira_settings", query={})
        auth_jira = JIRA(basic_auth=(jira_settings['email'], jira_settings['password']),
                         server=jira_settings['server'])
        release_notes = "{} has been deployed to production! Release notes:\n".format(version)
        issues = auth_jira.search_issues("""fixVersion in ("{}")""".format(version))
        for issue in issues:
            release_notes = release_notes + str(issue) + " - " + auth_jira.issue(issue).fields.summary + "\n"
        return release_notes

    @classmethod
    def evaluate(cls, msg):
        pattern = re.compile("finished deploying branch.* version.* to production")
        if pattern.findall(msg):
            version = cls.get_latest_release()
            release_notes = Samples.get_release_notes(version)
            return release_notes
