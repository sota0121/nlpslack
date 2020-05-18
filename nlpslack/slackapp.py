# slackapiを使って所望の情報を取得するクラス(加工はしない)
import requests
import json
from tqdm import tqdm
import pandas as pd


class SlackApp:
    ch_list_url = 'https://slack.com/api/channels.list'
    ch_history_url = 'https://slack.com/api/channels.history'
    usr_list_url = 'https://slack.com/api/users.list'

    def __init__(self, ch_api_key, usr_api_key):
        # NEW members
        self.channels_info = []
        self.users_info = []
        self.messages_info = []
        # OLD members
        self.channelInfo = {}  # k: ch_name, v: ch_id
        self.messages_in_chs = {}
        self.userInfo = {}
        self.ch_api_token = str(ch_api_key)
        self.usr_api_token = str(usr_api_key)

    def load_save_channel_info(self, outdir: str):
        # slackAPI経由でchannel情報を取得してファイルに保存
        payload = {'token': self.ch_api_token}
        response = requests.get(SlackApp.ch_list_url, params=payload)
        if response.status_code == 200:
            json_data = response.json()
            if 'channels' in json_data.keys():
                self.channels_info = json_data['channels']
            with open(outdir + '/' + 'channel_info.json', 'w', encoding='utf-8') as f:
                json.dump(self.channels_info, f, indent=4, ensure_ascii=False)

    def load_save_user_info(self, outdir: str):
        # slackAPI経由でuser情報を取得してファイルに保存
        payload = {'token': self.usr_api_token}
        response = requests.get(SlackApp.usr_list_url, params=payload)
        if response.status_code == 200:
            json_data = response.json()
            if 'members' in json_data.keys():
                self.users_info = json_data['members']
            with open(outdir + '/' + 'user_info.json', 'w', encoding='utf-8') as f:
                json.dump(self.users_info, f, indent=4, ensure_ascii=False)

    def load_save_messages_info(self, outdir: str):
        # channel id list 作成
        channel_id_list = []
        for ch in self.channels_info:
            channel_id_list.append(ch['id'])
        # slackAPI経由でuser情報を取得してファイルに保存
        for ch_id in tqdm(channel_id_list, desc='[loading...]'):
            payload = {'token': self.ch_api_token, 'channel': ch_id}
            response = requests.get(SlackApp.ch_history_url, params=payload)
            if response.status_code == 200:
                json_data = response.json()
                msg_in_ch = {}
                msg_in_ch['channel_id'] = ch_id
                if 'messages' in json_data.keys():
                    msg_in_ch['messages'] = json_data['messages']
                else:
                    msg_in_ch['messages'] = ''
                self.messages_info.append(msg_in_ch)
        with open(outdir + '/' + 'messages_info.json', 'w', encoding='utf-8') as f:
            json.dump(self.messages_info, f, indent=4, ensure_ascii=False)  