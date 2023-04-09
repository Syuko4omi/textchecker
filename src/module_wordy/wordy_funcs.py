from typing import Union
import json


def create_wordy_expression_dict(
    wordy_expressions_file_path="src/module_wordy/wordy_expressions.jsonl",
) -> dict[str, list[str]]:
    # keyが冗長な表現、valueが置き換えるべき先の表現のリストであるような辞書を作る
    wordy_expressions = {}
    with open(wordy_expressions_file_path, "r") as f_r:
        for line in f_r:
            instance: dict = json.loads(line)
            wordy_expressions[instance["original_wordy_form"]] = instance[
                "simpler_form"
            ]
    sorted_wordy_expressions = {}
    for key, val in sorted(
        wordy_expressions.items(), key=lambda x: len(x[0]), reverse=True
    ):  # 「こと」よりも先に「ことができ」を拾いたいので、長いものから一致を探すためkey文字列の長い順にソートする
        sorted_wordy_expressions[key] = val
    return wordy_expressions


def find_wordy_expression(
    one_sentence: str, wordy_expression_dict: dict[str, list[str]]
) -> list[str]:
    # 文章中から冗長表現を抜き出す
    wordy_parts = []
    for key in wordy_expression_dict.keys():
        if len(one_sentence.split(key)) > 1:  # 冗長表現が文章の中にあった場合
            splitted_parts = one_sentence.split(key)  # その冗長表現を境界にして文章を分ける
            for idx in range(len(splitted_parts)):  # 文中に登場する順序を保ったまま、冗長表現を格納する
                wordy_parts.extend(
                    find_wordy_expression(splitted_parts[idx], wordy_expression_dict)
                )
                if idx != len(splitted_parts) - 1:
                    wordy_parts.append(key)
            break
    return wordy_parts


def wrapper_find_wordy_expression(
    one_sentence: str, wordy_expression_dict: dict[str, list[str]]
) -> tuple[list[str], list[str]]:
    # まわりくどい言い回しにアラートを出す
    wordy_expressions = find_wordy_expression(one_sentence, wordy_expression_dict)
    advice_list = []
    for wordy_expression in wordy_expressions:
        alternative_expressions = [
            f"{item}" for item in wordy_expression_dict[wordy_expression] if item != ""
        ]
        alt_candidates = (
            "・".join(alternative_expressions)
            if len(alternative_expressions) != 0
            else "-"
        )
        advice_list.append(f"代替候補： {alt_candidates}")
    return wordy_expressions, advice_list


def wordy_expression_checker(
    sentences: list[str], wordy_expression_dict: dict[str, list[str]], row_num: int
) -> tuple[list[Union[str, tuple[str, str, str]]], list[tuple[str, str]], list[str]]:
    annotated_text_list: list[Union[str, tuple[str, str, str]]] = []
    text_position_list = []
    advices_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        start_idx = 0  # 一文の中でどこまで読んだか（どこから次の冗長表現を探すか）
        problematic_parts, advice_list = wrapper_find_wordy_expression(
            one_sentence, wordy_expression_dict
        )
        if len(problematic_parts) > 0:
            for problematic_part, advice in zip(problematic_parts, advice_list):
                # 冗長な表現を文章の前の方から見つけていく
                problematic_part_start_idx = one_sentence.find(
                    problematic_part, start_idx
                )
                annotated_text_list.append(  # 問題の箇所の直前までを格納
                    one_sentence[start_idx:problematic_part_start_idx]
                )
                annotated_text_list.append((problematic_part, advice, "#009900"))
                start_idx = problematic_part_start_idx + len(problematic_part)
                text_position_list.append(
                    (f"{row_num+1}行目第{sentence_num+1}文", problematic_part)
                )
            annotated_text_list.append(one_sentence[start_idx:])
            advices_list.extend(advice_list)
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list, advices_list
