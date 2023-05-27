from typing import Union
import json

# 中身はwordy_funcs.pyとほぼ同じ


def create_tautological_expression_dict(
    tautological_expressions_file_path="src/module_wordy/tautological_expressions.jsonl",
) -> dict[str, list[str]]:
    # keyが重複表現、valueが置き換えるべき先の表現のリストであるような辞書を作る
    tautological_expressions = {}
    with open(tautological_expressions_file_path, "r") as f_r:
        for line in f_r:
            instance: dict = json.loads(line)
            tautological_expressions[instance["original_tautological_form"]] = instance[
                "non_tautological_form"
            ]
    return tautological_expressions


def find_tautological_expression(
    one_sentence: str, tautological_expression_dict: dict[str, list[str]]
) -> list[str]:
    # 文章中から重複表現を抜き出す
    tautological_parts = []
    for key in tautological_expression_dict.keys():
        if len(one_sentence.split(key)) > 1:  # 重複表現が文章の中にあった場合
            splitted_parts = one_sentence.split(key)  # その重複表現を境界にして文章を分ける
            for idx in range(len(splitted_parts)):  # 文中に登場する順序を保ったまま、重複表現を格納する
                tautological_parts.extend(
                    find_tautological_expression(
                        splitted_parts[idx], tautological_expression_dict
                    )
                )
                if idx != len(splitted_parts) - 1:
                    tautological_parts.append(key)
            break
    return tautological_parts


def wrapper_find_tautological_expression(
    one_sentence: str, tautological_expression_dict: dict[str, list[str]]
) -> tuple[list[str], list[str]]:
    # 重複した言い回しにアラートを出す
    tautological_expressions = find_tautological_expression(
        one_sentence, tautological_expression_dict
    )
    advice_list = []
    for tautological_expression in tautological_expressions:
        alternative_expressions = [
            f"{item}"
            for item in tautological_expression_dict[tautological_expression]
            if item != ""
        ]
        alt_candidates = (
            "・".join(alternative_expressions)
            if len(alternative_expressions) != 0
            else "-"
        )
        advice_list.append(f"代替候補： {alt_candidates}")
    return tautological_expressions, advice_list


def tautological_expression_checker(
    sentences: list[str],
    tautological_expression_dict: dict[str, list[str]],
    row_num: int,
) -> tuple[list[Union[str, tuple[str, str, str]]], list[tuple[str, str]], list[str]]:
    annotated_text_list: list[Union[str, tuple[str, str, str]]] = []
    text_position_list = []
    advices_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        start_idx = 0  # 一文の中でどこまで読んだか（どこから次の重複表現を探すか）
        problematic_parts, advice_list = wrapper_find_tautological_expression(
            one_sentence, tautological_expression_dict
        )
        if len(problematic_parts) > 0:
            for problematic_part, advice in zip(problematic_parts, advice_list):
                # 重複な表現を文章の前の方から見つけていく
                problematic_part_start_idx = one_sentence.find(
                    problematic_part, start_idx
                )
                annotated_text_list.append(  # 問題の箇所の直前までを格納
                    one_sentence[start_idx:problematic_part_start_idx]
                )
                annotated_text_list.append((problematic_part, advice, "#009000"))
                start_idx = problematic_part_start_idx + len(problematic_part)
                text_position_list.append(
                    (f"{row_num+1}行目第{sentence_num+1}文", problematic_part)
                )
            annotated_text_list.append(one_sentence[start_idx:])
            advices_list.extend(advice_list)
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list, advices_list
