from commons.database import Database


class MessageLog(object):
    def __init__(self, trigger_ts, gif_ts, trigger_user):
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
        return cls(**result)
