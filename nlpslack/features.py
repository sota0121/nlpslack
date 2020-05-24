from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import json
from gensim.models import Word2Vec
from pathlib import Path


# tf-idf : one key given by one document
#
# - *input ... ndarray or pd.DataFrame
#   ndarray(
#    ('key0', 'w00 w01 w02 w03 w04 w05'),
#    ('key1', 'w06 w07 w08 w09'),
#    ('key2', 'w10 w11 w12 w13 w14 w15 w16 w17 w18'),
#     :
#   )
# - *output
#   {
#     'key0': {'w04': 0.89, 'w02': 0.76, 'w00': 0.54, ...},
#     'key1': {'w09': 0.67, 'w06': 0.32, 'w07': 0.10, ...},
#     'key2': {'w17': 0.77, 'w18': 0.45, 'w10': 0.28, ...},
#      :
#   }
class TfIdf:
    def __init__(self):
        super().__init__()
        self._vectorizer = TfidfVectorizer(token_pattern=u'(?u)\\b\\w+\\b')

    def extraction_important_words(self, dict_grouped: dict) -> dict:
        # calc tf-idf
        bow_vec = self._vectorizer.fit_transform(dict_grouped.values())
        bow_array = bow_vec.toarray()
        bow_df = pd.DataFrame(bow_array,
                              index=dict_grouped.keys(),
                              columns=self._vectorizer.get_feature_names())
        # extract high score words -> dict
        score_word_dic = self.extract_high_score_words(
            self._vectorizer.get_feature_names(), bow_df, dict_grouped.keys())
        return score_word_dic

    def extract_high_score_words(self, feat_names: list, bow_df: pd.DataFrame,
                                 keys: list) -> dict:
        # > 行ごとにみていき、重要単語を抽出する(tfidf上位X個の単語)
        dict_important_words_by_key = {}
        for uid, (i, scores) in zip(keys, bow_df.iterrows()):
            # 当該ユーザーの単語・tfidfスコアのテーブルを作る
            words_score_tbl = pd.DataFrame()
            words_score_tbl['scores'] = scores
            words_score_tbl['words'] = feat_names
            # tfidfスコアで降順ソートする
            words_score_tbl = words_score_tbl.sort_values('scores',
                                                          ascending=False)
            words_score_tbl = words_score_tbl.reset_index()
            # extract : tf-idf score > 0.001
            important_words = words_score_tbl.query('scores > 0.001')
            # 当該キーの辞書作成 'uid0': {'w0': 0.9, 'w1': 0.87}
            d = {}
            for i, row in important_words.iterrows():
                d[row.words] = row.scores
            # 当該キーの辞書にワードが少なくとも一つ以上ある場合のみテーブルに追加
            if len(d.keys()) > 0:
                dict_important_words_by_key[uid] = d
        return dict_important_words_by_key


class Word2Vector:
    def __init__(self):
        super().__init__()
        here = str(Path(__file__).parent)
        self.model = Word2Vec.load(here + '/../data/model/wiki.model')

    def get_similar_words(self, w: str):
        results = self.model.wv.most_similar(positive=[w])
        for result in results:
            print(result)
