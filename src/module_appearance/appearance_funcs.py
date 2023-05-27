from typing import Union
import re


def find_hankaku_num_eng(one_sentence: str) -> list[str]:
    point_out_list = re.findall("[A-Za-z0-9]+", one_sentence)
    return point_out_list


def find_zenkaku_num_eng(one_sentence: str) -> list[str]:
    point_out_list = re.findall("[Ａ-Ｚａ-ｚ０-９]+", one_sentence)
    return point_out_list


def find_hankaku_kana(one_sentence: str) -> list[str]:
    point_out_list = re.findall("[ｦ-ﾟ]+", one_sentence)
    return point_out_list


def find_hankaku_kigou(one_sentence: str) -> list[str]:
    point_out_list = re.findall("[ -/:-@\[-~]+", one_sentence)
    return point_out_list


def appearance_checker(sentences: list[str], row_num: int, objective: str = "半角英数字"):
    correspondence_dict = {
        "半角英数字": find_hankaku_num_eng,
        "全角英数字": find_zenkaku_num_eng,
        "半角カタカナ": find_hankaku_kana,
        "半角記号": find_hankaku_kigou,
    }
    appearance_function = correspondence_dict[objective]
    annotated_text_list: list[Union[str, tuple[str, str, str]]] = []
    text_position_list = []
    advice_list: list[str] = []

    for sentence_num, one_sentence in enumerate(sentences):
        start_idx = 0  # 一文の中でどこまで読んだか（どこから次の冗長表現を探すか）
        problematic_parts = appearance_function(one_sentence)
        if len(problematic_parts) > 0:
            for problematic_part in problematic_parts:
                # 冗長な表現を文章の前の方から見つけていく
                problematic_part_start_idx = one_sentence.find(
                    problematic_part, start_idx
                )
                annotated_text_list.append(  # 問題の箇所の直前までを格納
                    one_sentence[start_idx:problematic_part_start_idx]
                )
                annotated_text_list.append((problematic_part, objective, "#009900"))
                start_idx = problematic_part_start_idx + len(problematic_part)
                text_position_list.append(
                    (f"{row_num+1}行目第{sentence_num+1}文", problematic_part)
                )
            annotated_text_list.append(one_sentence[start_idx:])
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list, advice_list
