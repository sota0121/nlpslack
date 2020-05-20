import os
import json
from pathlib import Path
import slackapp as sa
from db import Database
import sys
import argparse
import pandas as pd
from preprocessing import clean_msg
from preprocessing import MorphologicalAnalysis as manalyzer
from tqdm import tqdm

SCRIPT_DIR = str(Path(__file__).resolve().parent) + '/'
CREDENTIALS_PATH = SCRIPT_DIR + '../data/conf/credentials.json'
RAWDATA_PATH = SCRIPT_DIR + '../data/'
CHANNEL_INFO_PATH = SCRIPT_DIR + '../data/channel_info.json'
USER_INFO_PATH = SCRIPT_DIR + '../data/user_info.json'
MESSAGE_INFO_PATH = SCRIPT_DIR + '../data/messages_info.json'


# slack mesage extraction with slackapp
def slack_msg_extraction(credentials_path: str, outdir: str) -> bool:
    # load api key
    p = Path(credentials_path)
    if not p.exists():
        return False
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)
    # load info from slack via slack api
    app = sa.SlackApp(credentials['channel_api_key'],
                      credentials['user_api_key'])
    print('load slack info channels')
    app.load_save_channel_info(outdir)
    print('load slack info users')
    app.load_save_user_info(outdir)
    print('load slack info messages')
    app.load_save_messages_info(outdir)
    return True


# load json as dict
def _load_json_as_dict(fpath: str) -> dict:
    with open(fpath, 'r', encoding='utf-8') as f:
        _dict = json.load(f)
    return _dict


# show channels info
def show_slack_channels(channel_info_path: str) -> bool:
    ch_info_dict = _load_json_as_dict(channel_info_path)
    ch_name_list = [x['name'] for x in ch_info_dict]
    for i, ch_name in enumerate(ch_name_list):
        print(i, ': ', ch_name)
    return True


def _slack_channels_list(channel_info_path: str, excluding: list):
    ch_info_dict = _load_json_as_dict(channel_info_path)
    ch_name_list = [x['name'] for x in ch_info_dict]
    target_ch_list = [
        ch for i, ch in enumerate(ch_name_list) if i not in excluding
    ]
    return target_ch_list


# cleaning with preprocessing
def cleaning_msgs(msg_tbl: pd.DataFrame) -> pd.DataFrame:
    ser_msg = msg_tbl.msg
    clean_msg_list = [clean_msg(m) for m in ser_msg]
    msg_tbl.msg = pd.Series(clean_msg_list)
    return msg_tbl


# morphological_analysis  with preprocessing
def manalyze_msgs(msg_tbl: pd.DataFrame) -> pd.DataFrame:
    ma = manalyzer()
    ser_msg = msg_tbl.msg
    clean_msg_list = [
        ma.get_wakati_str(str(m)) for m in tqdm(ser_msg, desc='[wakati]')
    ]
    msg_tbl.msg = pd.Series(clean_msg_list)
    return msg_tbl


# normalization  with preprocessing
# stop word removal  with preprocessing
# important word extraction with features
# make wordcloud with visualization
'''
*** Flow ***
IN  > python main.py 1 --term lw
PROC> - get info via slack api (require: credentials.json)
OUT > load slack info (channels, users, messages)
OUT > select NOT target channels' number (sep space)
OUT > 0. general
OUT > 1. random
OUT > 2. newbie ...
IN  > 0 1
OUT > Target channels: newbie/...
PROC> save target channels as target_channels.csv
OUT > cleaning messages ...
OUT > morphological analysis ...
OUT > normalization ...
OUT > stop word removal ...
OUT > tf-idf scoring ...
OUT > generate wordcloud images ...
OUT > [wordcloud] ■■■■■----------- (6/13) <=tqdm
OUT > terminate
'''


def main(mode: int, term: str, update_slack_info: int):
    # get info via slack api (require: credentials.json)
    if update_slack_info == 1:
        ret = slack_msg_extraction(CREDENTIALS_PATH, RAWDATA_PATH)
        if ret is not True:
            sys.exit(1)

    # NOT target channels selection
    show_slack_channels(CHANNEL_INFO_PATH)
    print('----------------------------')
    not_targets = input('select NOT target channel numbers (sep space)')
    not_target_list = not_targets.split(' ')
    not_target_list = [int(i) for i in not_target_list]
    target_chname_list = _slack_channels_list(CHANNEL_INFO_PATH,
                                              excluding=not_target_list)
    print(target_chname_list)

    # make tables
    usr_dict = _load_json_as_dict(USER_INFO_PATH)
    ch_dict = _load_json_as_dict(CHANNEL_INFO_PATH)
    msg_dict = _load_json_as_dict(MESSAGE_INFO_PATH)
    database = Database()
    database.mk_tables(usr_dict, ch_dict, msg_dict, target_chname_list)
    print(database.usr_table.head(2))
    print(database.ch_table.head(2))
    print(database.msg_table.head(100))
    print('------')

    # cleaning
    database.msg_table = cleaning_msgs(database.msg_table)
    print(database.msg_table.head(100))

    # morphological analysis
    database.msg_table = manalyze_msgs(database.msg_table)
    print(database.msg_table.head(100))


if __name__ == "__main__":
    # ------------------------------------------------
    # set args
    # ------------------------------------------------
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",
                        help="0: wordcloud by user, 1:wordcloud by term",
                        type=int)
    parser.add_argument("--term",
                        help="w: term is week, m: term is month",
                        type=str)
    parser.add_argument("--us",
                        help="update info via slack api, default:1",
                        default=1,
                        type=int)
    args = parser.parse_args()

    # ------------------------------------------------
    # parse args
    # ------------------------------------------------
    mode = args.mode
    if (mode != 0) and (mode != 1):
        print('invalid args mode. please execute with -h opt.')
        sys.exit(1)
    term = args.term
    if mode == 1:
        if (term != 'w') and (term != 'm'):
            print('invalid arg --term. please execute with -h opt.')
            sys.exit(1)
    update_slack_info = args.us

    # ------------------------------------------------
    # main process
    # ------------------------------------------------
    main(mode, term, update_slack_info)
