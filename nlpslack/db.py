import os
from pathlib import Path
import json
import pandas as pd
from google.cloud import bigquery


class Database:
    def __init__(self):
        super().__init__()
        self._usr_table = pd.DataFrame()
        self._ch_table = pd.DataFrame()
        self._msg_table = pd.DataFrame()

    # property
    @property
    def usr_table(self) -> pd.DataFrame():
        return self._usr_table

    @property
    def ch_table(self) -> pd.DataFrame():
        return self._ch_table

    @property
    def msg_table(self) -> pd.DataFrame():
        return self._msg_table

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
        self._msg_table = pd.DataFrame({
            'ch_id': ch_id_list,
            'msg': msg_list,
            'uid': uid_list,
            'timestamp': ts_list
        })
        # only save target channels
        target_chid_list = self._ch_table.ch_id.values.tolist()
        self._msg_table = self._msg_table.query('ch_id in @target_chid_list')
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
