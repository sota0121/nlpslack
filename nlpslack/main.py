import os
import sys
import json
import argparse
from pathlib import Path

import pickle
import pandas as pd
from tqdm import tqdm

import slackapp as sa
from db import Database
from preprocessing import clean_msg
from preprocessing import MorphologicalAnalysis as manalyzer
from preprocessing import normarize_text
from preprocessing import maybe_download
from preprocessing import load_sw_definition
from preprocessing import remove_sw_from_text
from features import TfIdf
from features import Word2Vector
from visualization import wordcloud_from_score

__version__ = '0.0.1'

SCRIPT_DIR = str(Path(__file__).resolve().parent) + '/'
CREDENTIALS_PATH = SCRIPT_DIR + '../data/conf/credentials.json'
RAWDATA_PATH = SCRIPT_DIR + '../data/'
CHANNEL_INFO_PATH = SCRIPT_DIR + '../data/channel_info.json'
USER_INFO_PATH = SCRIPT_DIR + '../data/user_info.json'
MESSAGE_INFO_PATH = SCRIPT_DIR + '../data/messages_info.json'
STOPWORD_LIST_PATH = SCRIPT_DIR + '../data/stopwords.txt'
TFIDF_SCORE_FILE_PATH = SCRIPT_DIR + '../data/tfidf_scores.json'
VECTORIZED_CONTENT_PATH = RAWDATA_PATH + 'content_features.json'
WORDCLOUD_OUTROOT = RAWDATA_PATH
WORDCLOUD_FONT_PATH = SCRIPT_DIR + '../data/res/rounded-l-mplus-1c-regular.ttf'

SUB_COMMAND_STR_WC = 'wc'
SUB_COMMAND_STR_VEC = 'vec'
SUB_COMMAND_STR_SEARCH = 'search'


def main(argv):
    """Main program.

    Arguments:
      argv: command-line arguments, such as sys.argv
      (including the program name in argv[0]).

    Returns:
      Zero on successful program termination, non-zero otherwise.
    """
    args, parser = _ParseArguments(argv)
    if args.version:
        print('nlpslack {}'.format(__version__))
        return 0
    
    if hasattr(args, 'handler'):
        return args.handler(args)
    else:
        parser.print_help()
        return 1


def _command_wc(args):
    """Sub program: wordcloud

    Arguments:
        args: Parsed arguments

    Returns:
        Zero on successful program termination, non-zero otherwise.
    """
    mode = args.mode
    term = args.term
    fs = args.fs
    print('call sub-command wc', args)

    # Need Slack raw info for all process (if only fetch flg==1)
    if fs == 1:
        ret = slack_msg_extraction(CREDENTIALS_PATH, RAWDATA_PATH)
        if ret is not True:
            sys.exit(1)

    # User can select NOT target channel which analyze
    show_slack_channels(CHANNEL_INFO_PATH)
    print('----------------------------')
    not_targets = input('select NOT target channel numbers (sep space)')
    not_target_list = not_targets.split(' ')
    not_target_list = [int(i) for i in not_target_list]
    target_chname_list = _slack_channels_list(CHANNEL_INFO_PATH,
                                              excluding=not_target_list)
    print(target_chname_list)

    # make it easy to analyze with tidy tables
    usr_dict = _load_json_as_dict(USER_INFO_PATH)
    ch_dict = _load_json_as_dict(CHANNEL_INFO_PATH)
    msg_dict = _load_json_as_dict(MESSAGE_INFO_PATH)
    database = Database()
    database.mk_tables(usr_dict, ch_dict, msg_dict, target_chname_list)
    print(database.usr_table.head(2))
    print(database.ch_table.head(2))
    print(database.msg_table.head(100))
    print('------')

    # Removing noise as preparation
    database.msg_table = cleaning_msgs(database.msg_table)
    print(database.msg_table.head(100))

    # Get wakati for analysis each words
    database.msg_table = manalyze_msgs(database.msg_table)
    print(database.msg_table.head(100))

    # Reduce notation variant for improvment accuracy
    database.msg_table = normalize_msgs(database.msg_table)
    print(database.msg_table.msg.head(100))

    # Remove very general words for improvment accuracy
    database.msg_table = rmsw_msgs(database.msg_table)
    print(database.msg_table.msg.head(100))

    # After preprocessing, some messages come NaN
    database.dropna_msg_table()

    # Snapshot preprocessed table for not repeat preprocessing
    with open('msg_tbl.pickle', 'wb') as f:
        pickle.dump(database.msg_table, f)

    # The more important words, the larger fonts on wordcloud
    dict_msgs_by_ = {}
    if mode == 'u':
        dict_msgs_by_ = database.group_msgs_by_user()
    elif mode == 't':
        dict_msgs_by_ = database.group_msgs_by_term(term)
    vectorizer = TfIdf()
    score_word_dic = vectorizer.extraction_important_words(dict_msgs_by_)
    with open(TFIDF_SCORE_FILE_PATH, 'w') as f:
        json.dump(score_word_dic, f, ensure_ascii=False, indent=4)

    dir_name = 'wc_by_usr' if mode == 0 else 'wc_by_term'
    wc_outdir = WORDCLOUD_OUTROOT + dir_name
    p = Path(wc_outdir)
    if p.exists() is False:
        p.mkdir()
    wordcloud_from_score(score_word_dic, WORDCLOUD_FONT_PATH, wc_outdir)
    return 0


def _command_vec(args) -> int:
    opath = args.out
    print('call sub-command vec', args)
    return 0


def _command_search(args) -> int:
    key_word = args.word
    print('call sub-command search', args)
    return 0


def _ParseArguments(argv):
    """Parse the command line arguments.

    Arguments:
      argv: command-line arguments, such as sys.argv
        (including the program name in argv[0]).

    Returns:
      An object containing the arguments used to invoke the program.
    """

    parser = argparse.ArgumentParser(
        description='nlp sandbox with slack messages.')
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='show version number and exit')
    parser.add_argument(
        '-fs',
        default=1,
        type=int,
        help='if fetch slack info or not (default: 1)')

    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "wc" command
    parser_wc = subparsers.add_parser(
        SUB_COMMAND_STR_WC,
        help='Generate wordcloud image')
    parser_wc.add_argument(
        'mode',
        type=str,
        help='u: each user, t:each term (weekly or monthly)')
    parser_wc.add_argument(
        '-t',
        '--term',
        help='w: weekly, m: monthly')
    parser_wc.set_defaults(handler=_command_wc)

    # create the parser for the "vec" command
    parser_vec = subparsers.add_parser(
        SUB_COMMAND_STR_VEC,
        help="Vectorize the content of each user's post and save as KVS")
    parser_vec.add_argument(
        '-o',
        '--out',
        type=str,
        default=VECTORIZED_CONTENT_PATH,
        help='output kvs path (*.json)')
    parser_vec.set_defaults(handler=_command_vec)

    # create the parser for the "search" command
    parser_search = subparsers.add_parser(
        SUB_COMMAND_STR_SEARCH,
        help='Recommend users who are interested in a given word')
    parser_search.add_argument(
        '-w',
        '--word',
        type=str,
        help="given word")
    parser_search.set_defaults(handler=_command_search)

    return parser.parse_args(argv[1:]), parser


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
    wakati_msg_list = [
        ma.get_wakati_str(str(m)) for m in tqdm(ser_msg, desc='[wakati]')
    ]
    msg_tbl.msg = pd.Series(wakati_msg_list)
    return msg_tbl


# normalization  with preprocessing
def normalize_msgs(msg_tbl: pd.DataFrame) -> pd.DataFrame:
    ser_msg = msg_tbl.msg
    norm_msg_list = [normarize_text(str(m)) for m in ser_msg]
    msg_tbl.msg = pd.Series(norm_msg_list)
    return msg_tbl


# stop word removal  with preprocessing
def rmsw_msgs(msg_tbl: pd.DataFrame) -> pd.DataFrame:
    # load stop words list
    maybe_download(STOPWORD_LIST_PATH)
    stopwords = load_sw_definition(STOPWORD_LIST_PATH)

    # remove stop words
    ser_msg = msg_tbl.msg
    rmsw_msg_list = [remove_sw_from_text(str(m), stopwords) for m in ser_msg]
    msg_tbl.msg = pd.Series(rmsw_msg_list)
    return msg_tbl


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


def run_main():
    sys.exit(main(sys.argv))


if __name__ == "__main__":
    run_main()
