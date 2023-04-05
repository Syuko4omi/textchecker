import os
import json
import numpy as np
from tqdm import tqdm
from utils import create_base_form_list, prepare_tokenizer, dict_add_append
from config import IGNORE_FILES, POS_LIST


def get_file_names(corpus_name: str = "livedoor_corpus") -> tuple[list[str], int]:
    # ライブドアコーパスのテキストファイルのパスを取得
    # https://www.rondhuit.com/download.html
    ret_file_names = []
    file_num = 0
    for folder_name in os.listdir(corpus_name):
        if folder_name not in IGNORE_FILES:
            file_names = os.listdir(f"{corpus_name}/{folder_name}")
            for file_name in file_names:
                ret_file_names.append(f"{corpus_name}/{folder_name}/{file_name}")
                file_num += 1
                if file_num > 500:
                    break
    return ret_file_names, file_num


if __name__ == "__main__":
    tokenizer = prepare_tokenizer()
    word_to_frequency: dict[str, dict[str, int]] = {
        pos_name: {} for pos_name in POS_LIST
    }
    file_names, file_num = get_file_names()
    for file_name in tqdm(file_names):
        with open(file_name, "r") as f_r:
            texts = f_r.read().splitlines()
            base_form_list = create_base_form_list(tokenizer, texts, None)
            # 一つのテキストファイルにつき一回まで数えるので、重複を除く
            base_form_list = list(set(map(tuple, base_form_list)))
            for base_form in base_form_list:
                word_to_frequency[base_form[0]] = dict_add_append(
                    word_to_frequency[base_form[0]], base_form[1]
                )
    idf_dict = {}  # idfスコア
    for pos_name in POS_LIST:
        idf_dict[pos_name] = {
            key: np.log(file_num / (val + 1)) + 1  # idfスコア
            for key, val in word_to_frequency[pos_name].items()
            if val != 1
        }  # 孤語を除いて辞書サイズを半分に
    with open("livedoor_corpus_dict.json", "w") as f_w:
        json.dump(idf_dict, f_w, ensure_ascii=False)
