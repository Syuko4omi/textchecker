import json
import numpy as np
from utils import create_base_form_list, prepare_tokenizer, dict_add_append


def create_tf_idf_dict(
    idf_dict: dict[str, float], word_to_frequency: dict[str, int]
) -> dict[str, float]:
    # idfスコアが入った辞書と、tfスコアの計算をするための単語ごとの頻度が入った辞書から、tf-idfスコアの計算をする

    const = np.log(7376 / 2) + 1  # 7376個ファイルがある
    word_to_tf_idf = {}

    for word, freq in word_to_frequency.items():
        if word in idf_dict:
            word_to_tf_idf[word] = np.log(freq + 1) * idf_dict[word]
        else:
            word_to_tf_idf[word] = np.log(freq + 1) * const
    word_to_tf_idf = sorted(word_to_tf_idf.items(), key=lambda x: x[1], reverse=True)
    return word_to_tf_idf


if __name__ == "__main__":
    word_to_frequency = {}
    tokenizer = prepare_tokenizer()
    file_name = "../hoge.txt"

    with open("livedoor_corpus_dict.json", "r") as f_r:
        idf_dict = json.load(f_r)

    with open(file_name, "r") as f_r:
        texts = f_r.read().splitlines()

    base_form_list = create_base_form_list(tokenizer, texts, pos_option=None)
    for base_form in base_form_list:
        word_to_frequency = dict_add_append(word_to_frequency, base_form)

    word_to_tf_idf = create_tf_idf_dict(idf_dict, word_to_frequency)

    print(word_to_tf_idf[:50])
