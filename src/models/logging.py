from commons.database import Database
import re
import time


class Logging(object):

    @staticmethod
    def add_entry(data):
        database = Database()
        database.initialize()
        database.insert("logging", data)

    @staticmethod
    def log_staging_deploy(msg):
        pattern = re.compile("finished deploying branch.* version.* to staging")
        if pattern.findall(msg):
            version = msg.split("branch")[1].split("version")[0].strip()
            database = Database()
            database.initialize()
            database.insert(collection="version_record",
                            data={
                                "version": version,
                                "time": int(time.time())
                            })