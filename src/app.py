# coding: utf-8
from flask import Flask, request, Response, make_response
from models.slack_commands import SlackCommands
from models.logging import Logging
from models.message_log import MessageLog
from models.samples import Samples
import unicodedata
from urllib.parse import urlencode
import hmac
import hashlib
import time
import re

import json

app = Flask(__name__)


@app.route("/release_bot/begin_auth", methods=["GET"])
def pre_install():
    return '''
      <a href="https://slack.com/oauth/authorize?scope={0}&client_id={1}">
          Add to Slack
      </a>
  '''.format(SlackCommands.get_app_credentials()["SLACK_OAUTH_SCOPE"],
             (SlackCommands.get_app_credentials()["SLACK_BOT_CLIENT_ID"]))


@app.route("/release_bot/finish_auth", methods=["GET", "POST"])
def post_install():
    if 'error' in request.args:
        return Response("It didn't work!")
    # Retrieve the auth code from the request params
    else:
        auth_code = request.args['code']
        # An empty string is a valid token for this request
        auth_response = SlackCommands.slack_token_request(auth_code)
        try:
            token = SlackCommands.get_token_from_database(team_id=auth_response['team_id'],
                                                          user_id=auth_response['user_id'])
            token.update_token(auth_response)
        except TypeError:
            token = SlackCommands()
            token.add_token(auth_response)
        return Response('It worked!')


@app.route('/release_bot/events', methods=['POST'])
def events():
    if authenticate_request(request):
        event_data = json.loads(request.data.decode('utf-8'))
        # Echo the URL verification challenge code back to Slack
        Logging.add_entry(event_data)
        if "challenge" in event_data:
            return make_response(
                event_data.get("challenge"), 200, {"content_type": "application/json"}
               )
        print("event data: {}".format(event_data))
        channel = "GCPJJ4G3U"
        try:
            if event_data['event']['subtype'] == 'message_deleted':
                delete_gif(event_data, channel)
        except KeyError:
            if all([("event" in event_data),
                    (event_data['event']['channel'] == channel),
                    (event_data['event']['type'] == "message"),
                    (Samples.evaluate(event_data['event']['text']))]):
                send_gif(event_data, channel)
            elif all([("event" in event_data),
                      (event_data['event']['channel'] == "DDCL7GCV7"),
                      (event_data['event']['user'] == "U1V9CPH89")]):
                print("got here")
                if add_sample(event_data=event_data, channel=channel):
                    SlackCommands.send_message(team_id=event_data['team_id'],
                                               channel="DDCL7GCV7",
                                               message="I gotchu fam :+1:")
                else:
                    SlackCommands.send_message(team_id=event_data['team_id'],
                                               channel="DDCL7GCV7",
                                               message="Already added :D")

        finally:
            return json.dumps({'success': True}), 200, {"content_type": "application/json"}
    else:
        return json.dumps({'success': False}), 401, {"content_type": "application/json"}


def send_gif(event_data, channel):
    if MessageLog.get_entry_by_ts(event_data['event']['event_ts']) is None:
        response = SlackCommands.send_gif(team_id=event_data['team_id'], channel=channel)
        print("response to sent message: {}".format(response))
        message = MessageLog(trigger_ts=event_data['event']['event_ts'],
                             gif_ts=response['ts'])
        print("message log entry: {}".format(message.json()))
        message.add_entry()


def delete_gif(event_data, channel):
    delete_check = MessageLog.get_entry_by_ts(event_data['event']['previous_message']['ts'])
    print("delete check result: {}".format(delete_check))
    if delete_check is not None:
        SlackCommands.delete_message(team_id=event_data['team_id'], channel_id=channel, ts=delete_check.gif_ts)


def add_sample(event_data, channel):
    print("trying..")
    message = event_data['event']['text']
    clean_msg = unicodedata.normalize('NFKC', message).lower().replace("\n", " ")
    existing_check = Samples.find_entry(clean_msg)
    if existing_check is not None:
        return False
    else:
        sample = Samples(text=clean_msg)
        sample.add_entry()
        send_gif(event_data=event_data, channel=channel)
        return True


def authenticate_request(passed_request):
    ts = passed_request.headers['X-Slack-Request-Timestamp']
    if abs(int(ts) - time.time()) > 360:
        return False
    request_body = urlencode(json.loads(passed_request.data.decode('utf-8')))
    print(request_body)
    slack_signing_secret = SlackCommands.get_app_credentials()['signing_secret'].encode()
    print(slack_signing_secret)
    sig_basestring = ('v0:' + str(ts) + ":" + request_body).encode()
    print(sig_basestring)
    hash_digest = hmac.new(slack_signing_secret, msg=sig_basestring, digestmod=hashlib.sha256).hexdigest()
    print(hash_digest)
    my_signature = 'v0=' + hash_digest
    print(my_signature)
    slack_signature = request.headers['X-Slack-Signature']
    print(slack_signature)
    if hmac.compare_digest(my_signature, slack_signature):
        return True

# team_freedom = G5GB3E2UQ
# phill test = GCPJJ4G3U


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4500)
