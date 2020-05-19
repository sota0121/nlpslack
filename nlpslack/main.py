import json
from pathlib import Path
import slackapp as sa


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


if __name__ == "__main__":
    main()
