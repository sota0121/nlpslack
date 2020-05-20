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
    app = sa.SlackApp(credentials['channel_api_key'],
                      credentials['user_api_key'])
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


def main(mode: int, term: str):
    # -------------------------------------------------
    # -------------------------------------------------


    ret = slack_msg_extraction(CREDENTIALS_PATH, RAWDATA_PATH)
    print(ret)
    #db.bq_test()


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

    # ------------------------------------------------
    # main process
    # ------------------------------------------------
    main(mode, term)
