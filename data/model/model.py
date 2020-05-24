from gensim.models import word2vec
from pathlib import Path
import logging

SCRIPT_DIR = str(Path(__file__).resolve().parent) + '/'
DATASET_DIR = SCRIPT_DIR + 'dataset/'
WIKI_DATASET_NAME = 'wiki_wakati.txt'
WIKI_MODEL_NAME = 'wiki.model'


def train_model_with_wiki():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                        level=logging.INFO)
    sentences = word2vec.Text8Corpus(DATASET_DIR + WIKI_DATASET_NAME)

    model = word2vec.Word2Vec(sentences, size=200, min_count=20, window=15)
    model.save("./" + WIKI_MODEL_NAME)