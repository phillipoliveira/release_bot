from flask import Flask, request, Response, make_response
from models.slack_commands import SlackCommands
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
        except KeyError:
            token = SlackCommands()
            token.add_token(auth_response)
        return Response('It worked!')


@app.route('/release_bot/events', methods=['POST'])
def events():
    event_data = json.loads(request.data.decode('utf-8'))
    # Echo the URL verification challenge code back to Slack
    pattern = re.compile("rel_.* release notes")
    if "challenge" in event_data:
        return make_response(
            event_data.get("challenge"), 200, {"content_type": "application/json"}
           )
    try:
        if event_data['event']['subtype'] == 'message_deleted':
            return json.dumps({'success': True}), 200, {"content_type": "application/json"}
    except KeyError:
        if all([("event" in event_data),
                (event_data['event']['channel'] == "GCPJJ4G3U"),
                (event_data['event']['type'] == "message"),
                (pattern.findall(event_data['event']['text']))]):
            SlackCommands.send_raw_message(team_id=event_data['team_id'],channel="GCPJJ4G3U", text="good work!")
    finally:
        return json.dumps({'success': True}), 200, {"content_type": "application/json"}

# team_freedom = G5GB3E2UQ
# {'event_time': 1538668365, 'authed_users': ['U1V9CPH89'], 'team_id': 'T0JRP51QF', 'token': 'c5P54hYmXPH2OOKC4gFhqxLK', 'api_app_id': 'AD7G0J78D', 'type': 'event_callback', 'event': {'user': 'U1V9CPH89', 'text': '.', 'client_msg_id': 'b5d1460f-e896-4406-b69a-9fdc6dd9b9ea', 'channel_type': 'group', 'event_ts': '1538668365.000100', 'type': 'message', 'ts': '1538668365.000100', 'channel': 'G5GB3E2UQ'}, 'event_id': 'EvD7AXRW4A'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000)
