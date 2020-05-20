from tqdm import tqdm
from wordcloud import WordCloud


# --------------------------------------------------
# word cloud
# ------------
# input
#   {
#     'key0': {'w04': 0.89, 'w02': 0.76, 'w00': 0.54, ...},
#     'key1': {'w09': 0.67, 'w06': 0.32, 'w07': 0.10, ...},
#     'key2': {'w17': 0.77, 'w18': 0.45, 'w10': 0.28, ...},
#      :
#   }
# --------------------------------------------------
def wordcloud_from_score(word_score_dic: dict, fontpath: str, outdir: str):
    for key, d_word_score in tqdm(word_score_dic.items(), desc='[wordcloud]'):
        keyname = str(key).replace('/', '-')
        outpath = outdir + '/' + keyname + '.png'
        # gen
        wc = WordCloud(background_color='white',
                       font_path=fontpath,
                       width=900,
                       height=600,
                       collocations=False)
        wc.generate_from_frequencies(d_word_score)
        wc.to_file(outpath)
