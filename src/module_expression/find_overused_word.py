import json
import numpy as np
from utils import create_base_form_list, prepare_tokenizer, dict_add_append
from config import POS_LIST


def create_tf_idf_dict(
    idf_dict: dict[str, dict[str, float]], word_to_frequency: dict[str, dict[str, int]]
) -> dict[str, dict[str, float]]:
    # idfスコアが入った辞書と、tfスコアの計算をするための単語ごとの頻度が入った辞書から、tf-idfスコアの計算をする

    const = np.log(7376 / 2) + 1  # 7376個ファイルがある
    word_to_tf_idf: dict[str, dict[str, float]] = {
        pos_name: {} for pos_name in POS_LIST
    }

    for pos_name in POS_LIST:
        for word, freq in word_to_frequency[pos_name].items():
            if word in idf_dict[pos_name]:
                word_to_tf_idf[pos_name][word] = (
                    np.log(freq + 1) * idf_dict[pos_name][word]
                )
            else:
                word_to_tf_idf[pos_name][word] = np.log(freq + 1) * const

    return word_to_tf_idf


def sort_tf_idf_dict(
    word_to_tf_idf: dict[str, dict[str, float]], pos_list: list[str] = POS_LIST
) -> list[tuple[str, str, float]]:
    # tf-idfスコアの大きい順に並べる
    pos_word_score: list[tuple[str, str, float]] = []
    for pos in pos_list:
        word_score_dict = word_to_tf_idf[pos]
        for word, score in word_score_dict.items():
            pos_word_score.append((pos, word, score))

    pos_word_score.sort(key=lambda x: x[2], reverse=True)

    return pos_word_score


if __name__ == "__main__":
    word_to_frequency: dict[str, dict[str, int]] = {
        pos_name: {} for pos_name in POS_LIST
    }
    tokenizer = prepare_tokenizer()
    file_name = "../hoge.txt"

    with open("livedoor_corpus_dict.json", "r") as f_r:
        idf_dict = json.load(f_r)

    with open(file_name, "r") as f_r:
        texts = f_r.read().splitlines()

    base_form_list = create_base_form_list(tokenizer, texts, pos_option=None)
    for base_form in base_form_list:
        word_to_frequency[base_form[0]] = dict_add_append(
            word_to_frequency[base_form[0]], base_form[1]
        )

    word_to_tf_idf = create_tf_idf_dict(idf_dict, word_to_frequency)
    sorted_tf_idf_dict = sort_tf_idf_dict(word_to_tf_idf, ["名詞"])

    print(sorted_tf_idf_dict[:50])
