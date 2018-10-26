# coding: utf-8
from flask import Flask, request, Response, make_response
from models.slack_commands import SlackCommands
from models.logging import Logging
from models.message_log import MessageLog
from models.regex import Regex
import unicodedata
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


@app.route('/release_bot/learn', methods=['POST'])
def return_fact():
    # Echo the URL verification challenge code back to Slack
    response = app.response_class(
        response={"text": "I gotchu bro"},
        status=200,
        mimetype='application/json')
    return response


@app.route('/release_bot/events', methods=['POST'])
def events():
    event_data = json.loads(request.data.decode('utf-8'))
    # Echo the URL verification challenge code back to Slack
    pattern = re.compile(Regex.get_main_regex().regex)
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
                (pattern.findall(unicodedata.normalize('NFKC', event_data['event']['text'].lower().replace(" ", "").replace("\n", ""))))]):
            send_gif(event_data, channel)
        elif all([("event" in event_data),
                  (event_data['event']['channel'] == "DDCL7GCV7"),
                  (event_data['event']['user'] == "U1V9CPH89"),
                  (event_data['event']['channel'])]):
            if add_regex(event_data=event_data, channel=channel):
                SlackCommands.send_message(team_id=event_data['team_id'],
                                           channel=channel,
                                           message="I gotchu fam :+1:")
            else:
                SlackCommands.send_message(team_id=event_data['team_id'],
                                           channel=channel,
                                           message="something fucked up :D")

    finally:
        return json.dumps({'success': True}), 200, {"content_type": "application/json"}


def send_gif(event_data, channel):
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


def add_regex(event_data, channel):
    message = event_data['event']['text']
    clean_msg = unicodedata.normalize('NFKC', message).lower().replace(" ", "").replace("\n", "")
    regex = Regex(regex=clean_msg, type="sub")
    regex.add_entry()
    Regex.update_main_regex()
    send_gif(event_data=event_data, channel=channel)
    return True

# team_freedom = G5GB3E2UQ
# phill test = GCPJJ4G3U

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4500)
