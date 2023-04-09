import os
import json
import numpy as np
from tqdm import tqdm

from module_expression.preparation import (
    create_base_form_list,
    prepare_tokenizer,
    dict_add_append,
)
from module_expression.config import IGNORE_FILES, POS_LIST


def get_file_names(corpus_name: str = "livedoor_corpus") -> tuple[list[str], int]:
    # livedoorニュースコーパスのテキストファイルのパスを取得
    ret_file_names = []
    file_num = 0
    for folder_name in os.listdir(f"./data/{corpus_name}"):
        if folder_name not in IGNORE_FILES:
            file_names = os.listdir(f"./data/{corpus_name}/{folder_name}")
            for file_name in file_names:
                ret_file_names.append(f"./data/{corpus_name}/{folder_name}/{file_name}")
                file_num += 1
    return ret_file_names, file_num


def calculate_document_frequency(
    tokenizer, file_names: list[str]
) -> dict[str, dict[str, int]]:
    # document frequency（ある単語が登場するファイルの数）を数える
    word_to_document_frequency: dict[str, dict[str, int]] = {  # 語彙の見た目が同じでも品詞で区別する
        pos_name: {} for pos_name in POS_LIST
    }
    for file_name in tqdm(file_names):
        with open(file_name, "r") as f_r:
            texts = f_r.read().splitlines()
            base_form_list = create_base_form_list(tokenizer, texts, None)
            # 一つのテキストファイルにつき一回まで数えるので、重複を除く
            base_form_list = list(set(map(tuple, base_form_list)))
            for base_form in base_form_list:
                word_to_document_frequency[base_form[0]] = dict_add_append(
                    word_to_document_frequency[base_form[0]], base_form[1]
                )
    return word_to_document_frequency


def calculate_idf_score(
    word_to_document_frequency: dict[str, dict[str, int]]
) -> dict[str, dict[str, float]]:
    idf_dict: dict[str, dict[str, float]] = {  # 語彙の見た目が同じでも品詞で区別する
        pos_name: {} for pos_name in POS_LIST
    }
    for pos_name in POS_LIST:
        idf_dict[pos_name] = {
            key: np.log(file_num / (val + 1)) + 1  # idfスコア
            for key, val in word_to_document_frequency[pos_name].items()
            if val != 1
        }  # 孤語を除いて辞書サイズを半分に
    return idf_dict


if __name__ == "__main__":
    tokenizer = prepare_tokenizer()
    file_names, file_num = get_file_names()
    word_to_document_frequency = calculate_document_frequency(tokenizer, file_names)
    idf_dict = calculate_idf_score(word_to_document_frequency)  # idfスコア
    with open("./data/livedoor_corpus_dict.json", "w") as f_w:
        json.dump(idf_dict, f_w, ensure_ascii=False)
