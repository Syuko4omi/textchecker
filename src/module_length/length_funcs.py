from typing import Union
import re


def find_too_long_sentence(one_sentence: str, length_threshold=80) -> bool:
    # (デフォルト)一文が80文字以上の文章にはアラートを出す
    if len(one_sentence) >= length_threshold:
        return True
    else:
        return False


def find_too_much_punctuation(one_sentence: str, punctuation_num_threshold=4) -> bool:
    # （デフォルト）文中に読点が4つ以上あったら、その文にアラートを出す
    if one_sentence.count("、") >= punctuation_num_threshold:
        return True
    else:
        return False


def find_too_less_punctuation(one_sentence: str, continuous_threshold=50) -> list[str]:
    # （デフォルト）読点抜きで50文字以上連続する部分にはアラートを出す
    too_less_punctuation_parts = []
    parts = one_sentence.split("、")
    for part in parts:
        if len(part) >= continuous_threshold:
            too_less_punctuation_parts.append(part)
    return too_less_punctuation_parts


def lengthy_checker(
    sentences: list[str], row_num: int
) -> tuple[list[Union[str, tuple[str]]], list[str]]:
    # 画面上で表示するための情報と、長すぎる文章を検出した位置の入ったリストをそれぞれ返す
    annotated_text_list = []
    text_position_list = []
    advice_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        if find_too_long_sentence(one_sentence):
            annotated_text_list.append(
                (one_sentence, f"長い（{len(one_sentence)}文字）", "#ff0000")
            )
            text_position_list.append(
                (f"{row_num+1}行目第{sentence_num+1}文", one_sentence)
            )
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list, advice_list


def punctuation_num_checker(
    sentences: list[str], row_num: int
) -> tuple[list[Union[str, tuple[str]]], list[str]]:
    # 画面上で表示するための情報と、読点が多い文章を検出した位置の入ったリストをそれぞれ返す
    annotated_text_list = []
    text_position_list = []
    advice_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        if find_too_much_punctuation(one_sentence):
            annotated_text_list.append(
                (one_sentence, f"読点が多い（{one_sentence.count('、')}個）", "#ff1a1a")
            )
            text_position_list.append(
                (f"{row_num+1}行目第{sentence_num+1}文", one_sentence)
            )
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list, advice_list


def continuous_checker(
    sentences: list[str], row_num: int
) -> tuple[list[Union[str, tuple[str]]], list[str]]:
    # 画面上で表示するための情報と、読点が適切に入っていない文章を検出した位置の入ったリストをそれぞれ返す
    annotated_text_list = []
    text_position_list = []
    advice_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        problematic_parts = find_too_less_punctuation(one_sentence)  # 読点が適切に入っていない部分文字列
        if len(problematic_parts) == 0:  # 一文中に読点がちゃんと入っている場合はそのまま
            annotated_text_list.append(one_sentence)
            continue
        parts = re.split(r"(?<=、)", one_sentence)
        for part in parts:  # 読点で区切った文のそれぞれの部分について、読点が適切に入っていないかチェック
            if any(problematic_part in part for problematic_part in problematic_parts):
                annotated_text_list.append((part, f"読点がない（{len(part)}文字）", "#ff3333"))
                text_position_list.append((f"{row_num+1}行目第{sentence_num+1}文", part))
            else:
                annotated_text_list.append(part)
    return annotated_text_list, text_position_list, advice_list
