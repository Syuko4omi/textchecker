import json
import numpy as np

from module_expression.preparation import create_base_form_list, dict_add_append
from module_expression.config import POS_LIST, COLOR_LIST, WARNING_LIST


def create_tf_idf_dict(
    idf_dict: dict[str, dict[str, float]],
    word_to_frequency: dict[str, dict[str, int]],
    use_const: bool,
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
                if use_const:
                    word_to_tf_idf[pos_name][word] = np.log(freq + 1) * const
                else:
                    word_to_tf_idf[pos_name][word] = 0

    return word_to_tf_idf


def sort_tf_idf_dict(
    word_to_tf_idf: dict[str, dict[str, float]], pos_list: list[str] = POS_LIST
) -> list[tuple[str, str, float]]:
    # tf-idfスコアの大きい順に並べる
    # 引数のpos_listは、特定の品詞だけのリストを与えればそれに絞ってソートできる
    pos_word_score: list[tuple[str, str, float]] = []
    for pos in pos_list:
        word_score_dict = word_to_tf_idf[pos]
        for word, score in word_score_dict.items():
            pos_word_score.append((pos, word, score))

    pos_word_score.sort(key=lambda x: x[2], reverse=True)

    return pos_word_score


def find_problematic_part(text_list, tokenizer, pos_option=POS_LIST, use_const=True):
    word_to_frequency: dict[str, dict[str, int]] = {
        pos_name: {} for pos_name in POS_LIST
    }
    base_form_list = create_base_form_list(tokenizer, text_list, None)
    for base_form in base_form_list:
        word_to_frequency[base_form[0]] = dict_add_append(
            word_to_frequency[base_form[0]], base_form[1]
        )
    with open("src/module_expression/livedoor_corpus_dict.json", "r") as f_r:
        idf_dict = json.load(f_r)
    word_to_tf_idf = create_tf_idf_dict(idf_dict, word_to_frequency, use_const)
    sorted_tf_idf_dict = sort_tf_idf_dict(word_to_tf_idf)

    return sorted_tf_idf_dict[:20]


def overused_expression_checker(sentences, row_num, tokenizer, problematic_parts):
    annotated_text_list = []
    text_position_list = []
    advice_list = []
    problematic_parts = [problematic_part[:2] for problematic_part in problematic_parts]
    problematic_level_dict = {}
    for i in range(len(problematic_parts)):
        if i < len(problematic_parts) // 3:
            problematic_level_dict[problematic_parts[i]] = 0
        elif i < (len(problematic_parts) // 3) * 2:
            problematic_level_dict[problematic_parts[i]] = 1
        else:
            problematic_level_dict[problematic_parts[i]] = 2
    for sentence_num, one_sentence in enumerate(sentences):
        tokenized_sentence = tokenizer.tokenize(one_sentence)
        for token in tokenized_sentence:
            if (
                token.part_of_speech.split(",")[0],
                token.base_form,
            ) in problematic_parts:
                problematic_level = problematic_level_dict[
                    (token.part_of_speech.split(",")[0], token.base_form)
                ]
                advice_list.append(
                    (token.part_of_speech.split(",")[0], token.base_form)
                )
                annotated_text_list.append(
                    (
                        token.surface,
                        f"頻度：{WARNING_LIST[problematic_level]}",
                        COLOR_LIST[problematic_level],
                    )
                )
                text_position_list.append(
                    (f"{row_num+1}行目第{sentence_num+1}文", token.surface)
                )
            else:
                annotated_text_list.append(token.surface)
    return annotated_text_list, text_position_list, advice_list


"""
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
    sorted_tf_idf_dict = sort_tf_idf_dict(word_to_tf_idf)
    # sorted_tf_idf_dict = sort_tf_idf_dict(word_to_tf_idf, ["名詞"])

    print(sorted_tf_idf_dict[:50])
"""
