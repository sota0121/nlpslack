import os
import json
from pathlib import Path
import slackapp as sa
import db
import sys
import argparse


CREDENTIALS_PATH = '../data/conf/credentials.json'
RAWDATA_PATH = '../data/'


# slack mesage extraction with slackapp
def slack_msg_extraction(credentials_path: str, outdir: str) -> bool:
    # load api key
    p = Path(credentials_path)
    if not p.exists():
        return False
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)
    # load info from slack via slack api
    app = sa.SlackApp(
        credentials['channel_api_key'],
        credentials['user_api_key']
    )
    app.load_save_channel_info(outdir)
    app.load_save_user_info(outdir)
    app.load_save_messages_info(outdir)
    return True


# make message table with db and preprocessing
# cleaning with preprocessing
# morphological_analysis  with preprocessing
# normalization  with preprocessing
# stop word removal  with preprocessing
# important word extraction with features
# make wordcloud with visualization


def main():
    
    ret = slack_msg_extraction(CREDENTIALS_PATH, RAWDATA_PATH)
    print(ret)
    #db.bq_test()


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
if __name__ == "__main__":
    main()
