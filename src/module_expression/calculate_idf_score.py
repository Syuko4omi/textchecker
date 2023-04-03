import os
import json
import numpy as np
from tqdm import tqdm
from utils import create_base_form_list, prepare_tokenizer, dict_add_append


def get_file_names() -> tuple[list[str], int]:
    # ライブドアコーパスのテキストファイルのパスを取得
    unused_files = ["CHANGES.txt", "README.txt", "LICENCE.txt", ".DS_Store"]
    ret_file_names = []
    file_num = 0
    for folder_name in os.listdir("livedoor_corpus"):
        if folder_name not in unused_files:
            file_names = os.listdir(f"livedoor_corpus/{folder_name}")
            for file_name in file_names:
                ret_file_names.append(f"livedoor_corpus/{folder_name}/{file_name}")
                file_num += 1
    return ret_file_names, file_num


if __name__ == "__main__":
    tokenizer = prepare_tokenizer()
    word_to_frequency = {}
    file_names, file_num = get_file_names()
    for file_name in tqdm(file_names):
        with open(file_name, "r") as f_r:
            texts = f_r.read().splitlines()
            # 一つのテキストファイルにつき一回まで数える
            base_form_list = list(set(create_base_form_list(tokenizer, texts, None)))
            for base_form in base_form_list:
                word_to_frequency = dict_add_append(word_to_frequency, base_form)
    idf_dict = {
        key: np.log(file_num / (val + 1)) + 1  # idfスコア
        for key, val in word_to_frequency.items()
        if val != 1
    }  # 孤語を除いて辞書サイズを半分に
    with open("livedoor_corpus_dict.json", "w") as f_w:
        json.dump(idf_dict, f_w, ensure_ascii=False)
