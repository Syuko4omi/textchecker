from module_length import length_checker
import re
import streamlit as st
from annotated_text import annotated_text
import argparse


def create_sidebar():
    uploaded_files = st.sidebar.file_uploader(
        "テキストファイルを選んでください（今は使えません）", accept_multiple_files=False
    )
    show_elements = st.sidebar.radio("表示する要素を選んでください", ("長すぎる文", "読点が多い文", "読点がない文"))
    return uploaded_files, show_elements


def lengthy_checker(
    sentences: list[str], objective_func=length_checker.find_too_long_sentence
):
    annotated_text_list = []
    text_position_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        if objective_func(one_sentence):
            annotated_text_list.append(
                (one_sentence, f"長い（{len(one_sentence)}文字）", "#ff0000")
            )
            text_position_list.append((f"{row_num}行目第{sentence_num+1}文", one_sentence))
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list


def punctuation_num_checker(
    sentences: list[str], objective_func=length_checker.find_too_much_punctuation
):
    annotated_text_list = []
    text_position_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        if objective_func(one_sentence):
            annotated_text_list.append(
                (one_sentence, f"読点が多い（{one_sentence.count('、')}個）", "#ff1a1a")
            )
            text_position_list.append((f"{row_num}行目第{sentence_num+1}文", one_sentence))
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list


def continuous_checker(
    sentences: list[str], objective_func=length_checker.find_too_less_punctuation
):
    annotated_text_list = []
    text_position_list = []
    for sentence_num, one_sentence in enumerate(sentences):
        if len(objective_func(one_sentence)):
            parts = re.split(r"(?<=、)", one_sentence)
            problematic_parts = length_checker.find_too_less_punctuation(one_sentence)
            for part in parts:
                flag = False
                for problematic_part in problematic_parts:
                    if problematic_part in part:
                        flag = True
                        break
                if flag:
                    annotated_text_list.append(
                        (part, f"読点がない（{len(part)}文字）", "#ff3333")
                    )
                    text_position_list.append((f"{row_num}行目第{sentence_num+1}文", part))
                else:
                    annotated_text_list.append(part)
        else:
            annotated_text_list.append(one_sentence)
    return annotated_text_list, text_position_list


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_name", default="hoge.txt", help="put your text file name"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    element_to_func = {
        "長すぎる文": lengthy_checker,
        "読点が多い文": punctuation_num_checker,
        "読点がない文": continuous_checker,
    }
    st.set_page_config(layout="wide")  # ページの横幅をフルに使う
    uploaded_files, show_elements = create_sidebar()
    col1, col2, col3 = st.columns((6, 0.25, 3.75))  # col1は本文でcol3は指摘箇所を表示。col2は余白

    annotated_texts = []
    pos_list = []
    my_args = get_args()
    file_name = uploaded_files if uploaded_files is not None else my_args.file_name

    with col1:
        st.header("本文")
        with open(file_name, "r") as f:
            text_lists = f.read().splitlines()
            for row_num, text in enumerate(text_lists):
                sentences = re.split(r"(?<=。)", text)
                checker_function = element_to_func[show_elements]
                annotated_text_list, text_position_list = checker_function(sentences)
                annotated_texts += annotated_text_list
                pos_list += text_position_list
                annotated_texts.append(
                    "  \n"
                )  # Streamlitは改行記号の前に半角スペースが2つ必要 (https://github.com/streamlit/streamlit/issues/868)
        annotated_text(*annotated_texts)
    with col3:
        st.header("指摘箇所")
        for item in pos_list:
            st.write(f"{item[0]}  \n{item[1]}")
