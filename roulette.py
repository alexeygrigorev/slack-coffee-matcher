import os

import yaml
import json

import random

import requests

from typing import List, Tuple


SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

headers = {
    'Authorization': f'Bearer {SLACK_BOT_TOKEN}'
}

with open('config.yaml', 'rt') as f_in:
    config = yaml.safe_load(f_in)


message_template = config['roulette']['message']


def get_channel_participants(channel_id: str) -> List[str]:
    url = 'https://slack.com/api/conversations.members'

    params = {'channel': channel_id, 'limit': 100}
    members = []

    while True:
        response = requests.get(url, params=params, headers=headers)

        response.raise_for_status()
        response_json = response.json()

        members.extend(response_json['members'])

        response_metadata = response_json['response_metadata']
        next_cursor = response_metadata['next_cursor']

        if next_cursor == '':
            break

        params['cursor'] = next_cursor

    return members


def open_mpdm_group(user_1: str, user_2: str) -> str:
    url = 'https://slack.com/api/conversations.open'

    params = {
        'users': f'{user_1},{user_2}'
    }

    response = requests.post(url, params=params, headers=headers)
    response.raise_for_status()
    response_json = response.json()

    mpdm_channel_id = response_json['channel']['id']
    return mpdm_channel_id


def post_message(channel: str, message: str):
    url = 'https://slack.com/api/chat.postMessage'

    message_request = {
        "channel": channel,
        "blocks": [{
            "type": "section",
            "text": {"type": "mrkdwn", "text": message}
        }]
    }

    print(f'posting {message} to {channel}...')
    response = requests.post(url, json=message_request, headers=headers)
    response.raise_for_status()

    print(json.dumps(response.json()))


def find_pais(users: List[str]) -> List[Tuple[str, str]]:
    users_to_match = users.copy()
    random.shuffle(users_to_match)

    pairs = []

    while len(users_to_match) > 1:
        user1 = users_to_match.pop()
        user2 = users_to_match.pop()
        pairs.append((user1, user2))

    if len(users_to_match) == 1:
        last_user = users_to_match.pop()

        while True:
            idx = random.randint(0, len(users) - 1)
            if last_user == users[idx]:
                continue
            pairs.append((last_user, users[idx]))
            break

    return pairs


def chat_roulette_dm(user_1: str, user_2: str, channel_name: str):
    mpdm_channel_id = open_mpdm_group(user_1, user_2)
    message = message_template.format(
        USER1=user_1,
        USER2=user_2,
        CHANNEL_NAME=channel_name
    )
    post_message(mpdm_channel_id, message)


def run(channel: str):
    users = get_channel_participants(channel)
    pairs = find_pais(users)

    for user_1, user_2 in pairs:
        chat_roulette_dm(user_1, user_2, channel)


def lambda_handler(event, context):
    channel = event['channel']
    run(channel)

    return {
        'statusCode': 200,
        'body': 'ok'
    }
