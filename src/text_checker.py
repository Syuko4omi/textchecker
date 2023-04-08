from module_length import length_funcs
from module_wordy import wordy_funcs
from module_expression import overused_funcs, preparation

import re
import argparse
import streamlit as st
from annotated_text import annotated_text


def create_layout():
    st.set_page_config(layout="wide")  # ページの横幅をフルに使う
    uploaded_file = st.sidebar.file_uploader(
        "テキストファイルを選んでください", accept_multiple_files=False
    )
    show_element = st.sidebar.selectbox(
        "表示する要素を選んでください", ["長すぎる文", "読点が多い文", "読点がない文", "冗長な表現", "使われすぎな表現"]
    )

    return uploaded_file, show_element


def prepare_tools_for_analysis():
    wordy_expression_dict = wordy_funcs.create_wordy_expression_dict()
    tokenizer = preparation.prepare_tokenizer()
    return wordy_expression_dict, tokenizer


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_name", default="src/hoge.txt", help="put your text file name"
    )
    args = parser.parse_args()
    return args


def wrapper_function(
    show_element,
    sentences,
    row_num,
    wordy_expression_dict,
    tokenizer,
    overused_parts,
    problematic_level_dict,
):
    element_to_func = {
        "長すぎる文": length_funcs.lengthy_checker,
        "読点が多い文": length_funcs.punctuation_num_checker,
        "読点がない文": length_funcs.continuous_checker,
        "冗長な表現": wordy_funcs.wordy_expression_checker,
        "使われすぎな表現": overused_funcs.overused_expression_checker,
    }
    if show_element in ["長すぎる文", "読点が多い文", "読点がない文"]:
        annotated_text_list, text_position_list, advice_list = element_to_func[
            show_element
        ](sentences, row_num)
    elif show_element == "冗長な表現":
        (
            annotated_text_list,
            text_position_list,
            advice_list,
        ) = element_to_func[
            show_element
        ](sentences, wordy_expression_dict, row_num)
    else:
        (
            annotated_text_list,
            text_position_list,
            advice_list,
        ) = element_to_func[
            show_element
        ](sentences, row_num, tokenizer, overused_parts, problematic_level_dict)
    return annotated_text_list, text_position_list, advice_list


if __name__ == "__main__":
    my_args = get_args()
    uploaded_file, show_element = create_layout()

    annotated_texts = []  # 画面に表示するテキスト群
    pos_list = []  # 指摘した文章の場所
    advices_list = []  # 指摘の具体的な内容
    wordy_expression_dict, tokenizer = prepare_tools_for_analysis()
    f_r = open(my_args.file_name, "r")
    text_lists = (
        uploaded_file.read().decode("utf-8").splitlines()
        if uploaded_file is not None
        else f_r.read().splitlines()
    )
    f_r.close()
    overused_parts = overused_funcs.find_overused_part(  # 頻発する表現上位20件のリスト
        text_lists, tokenizer
    )
    problematic_level_dict = overused_funcs.overused_level_indicator(overused_parts)
    for row_num, text in enumerate(text_lists):  # 改行ごとに文章を処理する
        sentences = re.split(r"(?<=。)", text)  # 同じ行にある複数の文章がある場合は分ける
        annotated_text_list, text_position_list, advice_list = wrapper_function(
            show_element,
            sentences,
            row_num,
            wordy_expression_dict,
            tokenizer,
            overused_parts,
            problematic_level_dict,
        )
        annotated_texts += annotated_text_list
        pos_list += text_position_list
        advices_list += advice_list
        annotated_texts.append("  \n  \n")  # Streamlitは改行記号の前に半角スペースが2つ必要

    st.header("本文")
    annotated_text(*annotated_texts)

    with st.sidebar.expander(f"指摘箇所（{len(pos_list)}件）", expanded=True):
        if len(pos_list) == 0:
            st.write("指摘箇所はありません")
        if show_element in ["長すぎる文", "読点が多い文", "読点がない文"]:
            for item in pos_list:
                st.write(f"{item[0]}  \n{item[1]}")
        elif show_element == "冗長な表現":
            for item, advice in zip(pos_list, advices_list):
                st.write(f"{item[0]}  \n冗長表現： {item[1]}  \n{advice}")
        else:
            overused_expressions_dict = {
                overused_expression: advices_list.count(overused_expression)
                for overused_expression in overused_parts
            }
            for (pos, expression), freq in overused_expressions_dict.items():
                # TODO: ここで類義語サジェスト機能が欲しい
                st.write(f"（{pos}）{expression}：{freq}回")
