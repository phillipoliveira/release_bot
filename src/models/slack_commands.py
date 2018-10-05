from slackclient import SlackClient
from commons.database import Database
import time
import uuid
import re


class SlackCommands(object):
    def __init__(self,
                 access_token=None,
                 auth_code=None,
                 token_expiry_time=None,
                 team_id=None,
                 user_id=None,
                 _id=None):
        self.access_token = None if access_token is None else access_token
        self.auth_code = None if auth_code is None else auth_code
        self.token_expiry_time = None if token_expiry_time is None else token_expiry_time
        self.team_id= None if team_id is None else team_id
        self.user_id=None if user_id is None else user_id
        self._id = self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_slack_token(cls, team_id, user_id=None):
        database = Database()
        database.initialize()
        try:
            slack_token_object = cls.get_token_from_database(team_id=team_id,
                                                             user_id=user_id)
        except TypeError:
            print("Visit http://178.128.234.3:4500/release_bot/begin_auth to authorize this app")
            raise ValueError("Slack authorization failed")
        if slack_token_object.token_expiry_time is None:
            print("Visit http://178.128.234.3:4500/release_bot/begin_auth to authorize this app")
            raise ValueError("Slack authorization failed")
        elif int(slack_token_object.token_expiry_time) < int(time.time()):
            hook = cls.get_token_from_database(team_id=team_id,
                                               user_id=user_id)
            auth_response = hook.slack_token_request(hook.auth_code)
            try:
                hook.update_token(auth_response)
            except TypeError:
                hook.add_token(auth_response)
            return SlackClient(str(auth_response['access_token']))
        else:
            return SlackClient(str(slack_token_object.access_token))

    def update_token(self, auth_response):
        database = Database()
        database.initialize()
        self.access_token = auth_response['bot']['bot_access_token']
        self.team_id = auth_response['team_id']
        self.user_id = auth_response['user_id']
        numbers = re.compile('\d+(?:\.\d+)?')
        max_age = int(numbers.findall(auth_response['headers']['Strict-Transport-Security'])[0])
        self.token_expiry_time = int(time.time()) + max_age
        database.update(collection="slack_tokens",
                        query=({"team_id": self.team_id,
                                "user_id": self.user_id}),
                        update=self.json())

    def add_token(self, auth_response):
        database = Database()
        database.initialize()
        self.access_token = auth_response['bot']['bot_access_token']
        self.user_id = auth_response['user_id']
        self.team_id = auth_response['team_id']
        numbers = re.compile('\d+(?:\.\d+)?')
        max_age = int(numbers.findall(auth_response['headers']['Strict-Transport-Security'])[0])
        self.token_expiry_time = int(time.time()) + max_age
        database.insert(collection="slack_tokens",
                        data=self.json())

    def json(self):
        return({
            "_id": self._id,
            "access_token": self.access_token,
            "auth_code": self.auth_code,
            "token_expiry_time": self.token_expiry_time,
            "team_id": self.team_id,
            "user_id": self.user_id})

    @classmethod
    def slack_token_request(cls, auth_code):
        sc = SlackClient("")
        # Request the auth tokens from Slack
        auth_response = sc.api_call(
            "oauth.access",
            client_id=cls.get_app_credentials()["SLACK_BOT_CLIENT_ID"],
            client_secret=cls.get_app_credentials()["SLACK_BOT_CLIENT_SECRET"],
            code=auth_code
        )
        return auth_response

    @classmethod
    def get_token_from_database(cls, team_id, user_id=None):
        database = Database()
        database.initialize()
        if user_id is not None:
            credentials = database.find_one("slack_tokens", query=({"team_id": team_id,
                                                                         "user_id": user_id}))
        else:
            credentials = database.find_one("slack_tokens", query=({"team_id": team_id}))
        return cls(**credentials)

    @staticmethod
    def get_app_credentials():
        database = Database()
        database.initialize()
        result = database.find_one("slack_credentials", query=({}))
        return result

    @staticmethod
    def check_slack_token(test_token):
        slack_client_test = SlackClient(test_token)
        result = slack_client_test.api_call("auth.test")
        if result['ok'] is True:
            return True
        else:
            return False

    @staticmethod
    def authenticate_slack(team_id):
        slack_client = SlackCommands.get_slack_token(team_id=team_id)
        slack_client.api_call("api.test")
        slack_client.api_call("auth.test")

    @classmethod
    def send_raw_message(cls, team_id, channel, text):
        cls.get_slack_token(team_id).api_call("chat.postMessage", channel=channel, text=text)

# Deleting a message:
# slack = SlackCommands()
# slack.delete_message(channel_id='C0JS385LP', ts='1537797654.000100')
