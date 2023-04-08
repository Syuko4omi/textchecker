import json
import numpy as np

from module_expression.preparation import (
    create_base_form_list,
    dict_add_append,
    merge_parts,
)
from module_expression.config import POS_LIST, COLOR_LIST, WARNING_LIST


def create_tf_idf_dict(
    idf_dict: dict[str, dict[str, float]],
    word_to_frequency: dict[str, dict[str, int]],
    use_hapax: bool,
    doc_num: int,
) -> dict[str, dict[str, float]]:
    # idfスコアが入った辞書と、tfスコアの計算をするための単語ごとの頻度が入った辞書から、tf-idfスコアの計算をする

    # 文書中に出てこない単語のスコアを、文書中で1回出てきたものと同じとみなすかどうか
    hapax_idf_score = np.log(doc_num / 2) + 1 if use_hapax is True else 0
    word_to_tf_idf: dict[str, dict[str, float]] = {
        pos_name: {} for pos_name in POS_LIST  # 品詞名: {単語: スコア, ...}
    }

    for pos_name in POS_LIST:
        for word, freq in word_to_frequency[pos_name].items():
            if word in idf_dict[pos_name]:
                word_to_tf_idf[pos_name][word] = (
                    np.log(freq + 1) * idf_dict[pos_name][word]
                )
            else:
                word_to_tf_idf[pos_name][word] = np.log(freq + 1) * hapax_idf_score

    return word_to_tf_idf


def sort_tf_idf_dict(
    word_to_tf_idf: dict[str, dict[str, float]],
    pos_list: list[str] = POS_LIST,
    top_k: int = -1,
) -> list[tuple[str, str]]:
    # tf-idfスコアの大きい順に並べる
    # 引数のpos_listは、特定の品詞だけのリストを与えればそれに絞ってソートできる
    pos_word_score: list[tuple[str, str, float]] = []
    for pos in pos_list:
        word_to_score_dict = word_to_tf_idf[pos]
        for word, score in word_to_score_dict.items():
            pos_word_score.append((pos, word, score))

    pos_word_score.sort(key=lambda x: x[2], reverse=True)
    if top_k < 0:
        return [(pos, word) for (pos, word, score) in pos_word_score]
    else:
        return [(pos, word) for (pos, word, score) in pos_word_score[:20]]


def find_overused_part(
    text_list: list[str],
    tokenizer,
    pos_option: list[str] = POS_LIST,
    use_hapax: bool = False,
    doc_num: int = 7376,
    top_k: int = 20,
) -> list[tuple[str, str]]:
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
    word_to_tf_idf = create_tf_idf_dict(idf_dict, word_to_frequency, use_hapax, doc_num)
    sorted_tf_idf_list = sort_tf_idf_dict(
        word_to_tf_idf, pos_list=pos_option, top_k=top_k
    )

    return sorted_tf_idf_list


def overused_level_indicator(
    overused_parts: list[tuple[str, str]]
) -> dict[tuple[str, str], int]:
    problematic_level_dict = {}  # overused_partsの各要素に対して頻度の高低を数字で与える
    for i in range(len(overused_parts)):
        if i < len(overused_parts) // 3:
            problematic_level_dict[overused_parts[i]] = 0  # 高い
        elif i < (len(overused_parts) // 3) * 2:
            problematic_level_dict[overused_parts[i]] = 1  # 中くらい
        else:
            problematic_level_dict[overused_parts[i]] = 2  # 低い
    return problematic_level_dict


def overused_expression_checker(
    sentences, row_num, tokenizer, overused_parts, problematic_level_dict
):
    annotated_text_list = []
    text_position_list = []
    advice_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        tokenized_sentence = tokenizer.tokenize(one_sentence)
        for token in tokenized_sentence:
            pos = token.part_of_speech.split(",")[0]
            base_form = token.base_form
            surface = token.surface
            if (pos, base_form) in overused_parts:
                problematic_level = problematic_level_dict[(pos, base_form)]
                advice_list.append((pos, base_form))
                annotated_text_list.append(
                    (
                        surface,
                        f"頻度：{WARNING_LIST[problematic_level]}",
                        COLOR_LIST[problematic_level],
                    )
                )
                text_position_list.append((f"{row_num+1}行目第{sentence_num+1}文", surface))
            else:
                annotated_text_list.append(surface)
    annotated_text_list = merge_parts(annotated_text_list)
    return annotated_text_list, text_position_list, advice_list
