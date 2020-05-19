import os
from pathlib import Path
from google.cloud import bigquery
# make table
# connect db (bigquery)


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