# WordNet
# https://bond-lab.github.io/wnja/jpn/downloads.html
# https://www.yoheim.net/blog.php?q=20160201
# https://sucrose.hatenablog.com/entry/20120305/p1
# https://qiita.com/tchih11/items/ba6873b194fa50306823
# https://qiita.com/hiraski/items/50fea4c489bcc4823bc4
# https://qiita.com/pocket_kyoto/items/1e5d464b693a8b44eda5
# https://yottagin.com/?p=3112

# Word2Vec
# https://qiita.com/DancingEnginee1/items/b10c8ef7893d99aa53be
# https://github.com/shiroyagicorp/japanese-word2vec-model-builder


def getWords(conn, lemma):
    # ある単語の文字列(lemma)と一致する行を見つけ出す
    # 出力例：[(212666, 'jpn', 'イヌ', None, 'n')]
    cur = conn.execute("select * from word where lemma=?", (lemma,))
    return [row for row in cur]


def getSenses(conn, word):
    # ある単語から繋がる先の概念を、単語のidを指定することで見つけ出す
    # 出力例：[(synset='02084071-n', wordid=212666, lang='jpn', rank=None, lexid=None, freq=None, src='hand')]
    cur = conn.execute("select * from sense where wordid=?", (word[0],))
    return [row for row in cur]


def getWordsFromSynset(conn, synset):
    # 概念に紐づく単語を見つけ出す
    # 出力例：[(157603, 'jpn', '廻者', None, 'n'), (160841, 'jpn', '間諜', None, 'n'), ...]
    cur = conn.execute(
        "select word.* from sense, word where synset=? and word.lang=? and sense.wordid = word.wordid;",
        (synset, "jpn"),
    )
    return [row for row in cur]


def getSynset(conn, synset):
    # 概念が持つ意味を見つけ出す
    # 出力例：spy, canis_familiaris
    cur = conn.execute("select * from synset where synset=?", (synset,))
    return cur.fetchone()


def getWordsFromSenses(conn, sense):
    # 概念が持つ意味を見つけ出す
    # 出力例：{"spy":[...], "canis_familiaris":[...]}
    synonym = {}
    for s in sense:
        syns = getWordsFromSynset(conn, s[0])  # 概念id(synset)に紐づく単語を見つける
        # getSynset(s[0]) -> ('10641755-n', 'n', 'spy', 'eng30')
        synonym[getSynset(conn, s[0])[2]] = [sy[2] for sy in syns]  # 意味に紐づく類義語だけ出す
    return synonym


def getSynonym(conn, word):
    synonym = {}
    words = getWords(conn, word)  # 単語のidを見つけ出す
    if words:  # 単語がwordnetに登録されていた場合
        for w in words:
            sense = getSenses(conn, w)  # 単語が繋がる先の概念を見つけ出す
            s = getWordsFromSenses(conn, sense)  # 概念が持つそれぞれの意味に対して、類義語のリストを出す
            synonym = dict(list(synonym.items()) + list(s.items()))
    return synonym


def sort_word(gensim_model, connect, word) -> list[str]:
    word_dict = getSynonym(connect, word)
    L = []
    for key, word_list in word_dict.items():
        for cand in word_list:
            try:
                similarity = gensim_model.wv.similarity(word, cand)
                L.append((cand, similarity)) if cand != word else None
            except Exception:
                pass
    try:
        similar_words_in_word2vec = gensim_model.wv.most_similar(word)
        L += similar_words_in_word2vec
    except KeyError:
        pass
    L = list(set(L))
    L.sort(key=lambda x: x[1], reverse=True)
    ret = [item[0] for item in L if item[1] > 0.1]
    return ret
