import os
from pathlib import Path
import json
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=+9), 'JST')


class Database:
    def __init__(self):
        super().__init__()
        self._usr_table = pd.DataFrame()
        self._ch_table = pd.DataFrame()
        self._msg_table = pd.DataFrame()
        self._JST = timezone(timedelta(hours=+9), 'JST')

    # property
    @property
    def usr_table(self) -> pd.DataFrame():
        return self._usr_table

    @usr_table.setter
    def usr_table(self, value: pd.DataFrame):
        self._usr_table = value  # setter

    @property
    def ch_table(self) -> pd.DataFrame():
        return self._ch_table

    @ch_table.setter
    def ch_table(self, value: pd.DataFrame):
        self._ch_table = value  # setter

    @property
    def msg_table(self) -> pd.DataFrame():
        return self._msg_table

    @msg_table.setter
    def msg_table(self, value: pd.DataFrame):
        self._msg_table = value  # setter

    # method
    def _mk_usr_table(self, usr_dict: dict) -> bool:
        uid_list = []
        uname_list = []
        for usr_ditem in usr_dict:
            if usr_ditem['deleted'] is True:
                continue
            uid_list.append(usr_ditem['id'])
            uname_list.append(usr_ditem['profile']['real_name_normalized'])
        self._usr_table = pd.DataFrame({'uid': uid_list, 'uname': uname_list})
        return True

    def _mk_ch_table(self, ch_dict: dict, targets: list) -> bool:
        chid_list = []
        chname_list = []
        chnormname_list = []
        chmembernum_list = []
        for ch_ditem in ch_dict:
            chid_list.append(ch_ditem['id'])
            chname_list.append(ch_ditem['name'])
            chnormname_list.append(ch_ditem['name_normalized'])
            chmembernum_list.append(ch_ditem['num_members'])
        self._ch_table = pd.DataFrame({
            'ch_id': chid_list,
            'ch_name': chname_list,
            'ch_namenorm': chnormname_list,
            'ch_membernum': chmembernum_list
        })
        # only save target channels
        self._ch_table = self._ch_table.query('ch_name in @targets')
        return True

    def _mk_msg_table(self, msg_dict: dict) -> bool:
        ch_id_list = []
        msg_list = []
        uid_list = []
        ts_list = []
        tmp_tbl = pd.DataFrame()
        for msg_ditem in msg_dict:
            if 'channel_id' in msg_ditem.keys():
                ch_id = msg_ditem['channel_id']
            else:
                continue
            if 'messages' in msg_ditem.keys():
                msgs_in_ch = msg_ditem['messages']
            else:
                continue
            # get message in channel
            for i, msg in enumerate(msgs_in_ch):
                # if msg by bot, continue
                if 'user' not in msg:
                    continue
                ch_id_list.append(ch_id)
                msg_list.append(msg['text'])
                uid_list.append(msg['user'])  # botの場合はこのキーがない
                ts_list.append(msg['ts'])
        tmp_tbl = pd.DataFrame({
            'ch_id': ch_id_list,
            'msg': msg_list,
            'uid': uid_list,
            'timestamp': ts_list
        })
        # only save target channels
        target_chid_list = self._ch_table.ch_id.values.tolist()
        tmp_tbl = tmp_tbl.query('ch_id in @target_chid_list')
        # timestamp type str -> float
        tmp_tbl.timestamp = tmp_tbl.timestamp.astype(float)
        # sort by timestamp (last -> ago)
        self._msg_table = tmp_tbl.sort_values('timestamp', ascending=False)
        return True

    # targets = list of targetting channel names
    def mk_tables(self, usr_dict: dict, ch_dict: dict, msg_dict: dict,
                  targets: list) -> bool:
        print('make usr table')
        ret = self._mk_usr_table(usr_dict)
        if ret is not True:
            return False
        print('make ch table')
        ret = self._mk_ch_table(ch_dict, targets)
        if ret is not True:
            return False
        print('make msg table')
        ret = self._mk_msg_table(msg_dict)
        if ret is not True:
            return False

    # drop nan in msg tables
    def dropna_msg_table(self):
        self._msg_table = self._msg_table.dropna(axis='index')

    # grouping messages by users
    def group_msgs_by_user(self) -> dict:
        # 重複なしのuid一覧を取得
        ser_uid_unique = self._msg_table.drop_duplicates(subset='uid').uid
        # 重複なしuidごとにグルーピング(keyはuname)
        dict_msgs_by_user = {}
        for uid in ser_uid_unique:
            # 当該uidに該当する全wktmsgを取得
            extracted = self._msg_table.query('uid == @uid')
            # uid に対応する uname 取得
            target = self._usr_table.query('uid == @uid')
            if target.shape[0] != 0:  # non-active user does not exist
                uname = target.iloc[0]['uname']
            # key, value を出力用の辞書に追加
            dict_msgs_by_user[uname] = ' '.join(
                extracted.msg.dropna().values.tolist())
        return dict_msgs_by_user

    # grouping messages by terms
    def group_msgs_by_term(self, term: str) -> dict:
        # set term
        term_days = 8
        if term == 'm':
            term_days = 31
        print('group messages every {0} days'.format(term_days))
        # analyze timestamp
        origin_ts_dt = datetime.fromtimestamp(0, self._JST)
        now_in_sec = (datetime.now(self._JST) - origin_ts_dt).total_seconds()
        interval_days = timedelta(days=term_days)
        interval_seconds = interval_days.total_seconds()
        oldest_timestamp = self._msg_table['timestamp'].min()
        oldest_ts_dt = datetime.fromtimestamp(oldest_timestamp, self._JST)
        oldest_ts_in_sec = (oldest_ts_dt - origin_ts_dt).total_seconds()
        loop_num = (abs(now_in_sec - oldest_ts_in_sec) / interval_seconds) + 1
        # extract by term
        dict_msgs_by_term = {}
        df_tmp = self._msg_table
        now_tmp = now_in_sec
        for i in range(int(loop_num)):
            # make current term string
            cur_term_s = 'recent_{0}'.format(str(i).zfill(3))
            print(cur_term_s)
            # current messages
            _msg_table_cur = df_tmp.query(
                '@now_tmp - timestamp < @interval_seconds')
            _msg_table_other = df_tmp.query(
                '@now_tmp - timestamp >= @interval_seconds')
            # messages does not exist. break.
            if _msg_table_cur.shape[0] == 0:
                break
            # add current messages to dict
            dict_msgs_by_term[cur_term_s] = ' '.join(
                _msg_table_cur.msg.dropna().values.tolist())
            # update temp value for next loop
            now_tmp = now_tmp - interval_seconds
            df_tmp = _msg_table_other
        return dict_msgs_by_term


# ====== Future Database sample code ======
# make message table with db and preprocessing
def bq_test():
    script_dir = str(Path(__file__).resolve().parent)
    os.environ[
        'GOOGLE_APPLICATION_CREDENTIALS'] = script_dir + '/../data/conf/service_account.json'

    client = bigquery.Client()

    # Perform a query.
    QUERY = ('SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
             'WHERE state = "TX" '
             'LIMIT 10')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        print(row.name)
