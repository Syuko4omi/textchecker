from module_length import length_funcs
from module_wordy import wordy_funcs
import re
import streamlit as st
from annotated_text import annotated_text
import argparse


def create_layout():
    st.set_page_config(layout="wide")  # ページの横幅をフルに使う
    uploaded_file = st.sidebar.file_uploader(
        "テキストファイルを選んでください（今は使えません）", accept_multiple_files=False
    )
    show_element = st.sidebar.radio(
        "表示する要素を選んでください", ("長すぎる文", "読点が多い文", "読点がない文", "冗長な表現")
    )
    text_area, blank_area, advice_area = st.columns(
        (6, 0.25, 3.75)
    )  # text_areaは本文でadvice_areaは指摘箇所を表示。blank_areaは余白
    return uploaded_file, show_element, text_area, blank_area, advice_area


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_name", default="src/hoge.txt", help="put your text file name"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    element_to_func = {
        "長すぎる文": length_funcs.lengthy_checker,
        "読点が多い文": length_funcs.punctuation_num_checker,
        "読点がない文": length_funcs.continuous_checker,
        "冗長な表現": wordy_funcs.wordy_expression_checker,
    }

    uploaded_file, show_element, text_area, blank_area, advice_area = create_layout()

    annotated_texts = []  # 画面に表示するテキスト群
    pos_list = []  # 指摘した文章の場所
    advices_list = []  # 指摘の具体的な内容

    my_args = get_args()
    file_name = my_args.file_name
    wordy_expression_dict = wordy_funcs.create_wordy_expression_dict()

    with text_area:
        st.header("本文")
        f_r = open(file_name, "r")
        text_lists = (
            uploaded_file.read().decode("utf-8").splitlines()
            if uploaded_file is not None
            else f_r.read().splitlines()
        )
        f_r.close()
        for row_num, text in enumerate(text_lists):  # 改行区切り
            sentences = re.split(r"(?<=。)", text)  # 同じ行にある複数の文章
            checker_function = element_to_func[show_element]
            if show_element != "冗長な表現":
                (
                    annotated_text_list,
                    text_position_list,
                    advice_list,
                ) = checker_function(sentences, row_num)
            else:
                (
                    annotated_text_list,
                    text_position_list,
                    advice_list,
                ) = checker_function(sentences, wordy_expression_dict, row_num)
            annotated_texts += annotated_text_list
            pos_list += text_position_list
            advices_list += advice_list
            annotated_texts.append("  \n")  # Streamlitは改行記号の前に半角スペースが2つ必要
        annotated_text(*annotated_texts)

    with advice_area:
        st.header("指摘箇所")
        st.write(f"{len(pos_list)}件見つかりました")
        if show_element != "冗長な表現":
            for item in pos_list:
                st.write(f"{item[0]}  \n{item[1]}")
        else:
            for item, advice in zip(pos_list, advices_list):
                st.write(f"{item[0]}  \n冗長表現： {item[1]}  \n{advice}")
