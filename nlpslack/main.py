import os
import json
from pathlib import Path
import slackapp as sa
from google.cloud import bigquery



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
def bq_test():
    script_dir = str(Path(__file__).resolve().parent)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = script_dir + '/../data/conf/service_account.json'
    
    client = bigquery.Client()

    # Perform a query.
    QUERY = (
        'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
        'WHERE state = "TX" '
        'LIMIT 10')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        print(row.name)

# cleaning with preprocessing
# morphological_analysis  with preprocessing
# normalization  with preprocessing
# stop word removal  with preprocessing
# important word extraction with features
# make wordcloud with visualization


def main():
    #ret = slack_msg_extraction(CREDENTIALS_PATH, RAWDATA_PATH)
    #print(ret)
    bq_test()


if __name__ == "__main__":
    main()
