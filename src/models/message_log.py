from commons.database import Database
import uuid


class MessageLog(object):
    def __init__(self, trigger_ts, gif_ts, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.trigger_ts = trigger_ts
        self.gif_ts = gif_ts

    def json(self):
        return {"trigger_ts": self.trigger_ts,
                "gif_ts": self.gif_ts}

    def add_entry(self):
        database = Database()
        database.initialize()
        database.insert("message_log", self.json())

    @classmethod
    def get_entry_by_ts(cls, ts):
        database = Database()
        database.initialize()
        result = database.find_one("message_log", {"trigger_ts": ts})
        print("ts entry check result: {}".format(result))
        return cls(**result)


