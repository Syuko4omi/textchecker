import re
import argparse
import streamlit as st
from annotated_text import annotated_text
import sqlite3
import gensim

from module_length import length_funcs, proofread_with_chatgpt
from module_wordy import wordy_funcs
from module_expression import overused_funcs, preparation, get_synonym
from module_expression.config import POS_LIST


def create_layout():
    st.set_page_config(layout="wide")  # ページの横幅をフルに使う
    uploaded_file = st.sidebar.file_uploader("📝テキストファイル", accept_multiple_files=False)

    show_element = st.sidebar.selectbox(
        "⚙️表示する要素", ["長すぎる文", "読点が多い文", "読点がない文", "冗長な表現", "使われすぎな表現"]
    )

    selected_items = st.sidebar.multiselect(
        "💬品詞（「使われすぎな表現」を選んだ時のみ有効・複数選択可）",
        POS_LIST,
    )

    return uploaded_file, show_element, selected_items


def prepare_tools_for_analysis():
    wordy_expression_dict = wordy_funcs.create_wordy_expression_dict()
    tokenizer = preparation.prepare_tokenizer()
    return wordy_expression_dict, tokenizer


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_name", default="./data/demo.txt", help="put your text file name"
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
    uploaded_file, show_element, selected_items = create_layout()

    if selected_items == []:
        selected_items = POS_LIST

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
        text_lists, tokenizer, pos_option=selected_items
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

    with st.sidebar.expander(f"✅指摘箇所（{len(pos_list)}件）", expanded=True):
        if len(pos_list) == 0:
            st.write("指摘箇所はありません🤓")
        if show_element in ["長すぎる文", "読点が多い文", "読点がない文"]:
            for item in pos_list:
                st.write(f"### {item[0]}  \n{item[1]}")
        elif show_element == "冗長な表現":
            for item, advice in zip(pos_list, advices_list):
                st.write(f"### {item[0]}  \n冗長表現： {item[1]}  \n{advice}")
        else:
            conn = sqlite3.connect("./data/wnjpn.db")
            model = gensim.models.Word2Vec.load("./data/word2vec.gensim.model")
            overused_expressions_dict = {
                overused_expression: advices_list.count(overused_expression)
                for overused_expression in overused_parts
            }
            for (pos, expression), freq in overused_expressions_dict.items():
                ret_l = get_synonym.sort_word(model, conn, expression)
                cand = "・".join(ret_l)
                if len(cand) == 0:
                    cand = "-"
                st.write(f"### （{pos}）{expression}：{freq}回  \n  \n関連語：{cand}")

    with st.form(key="my_form", clear_on_submit=True):
        with st.sidebar:
            INPUT_LIMIT_LENGTH = 300
            long_sentence = st.text_input(
                label=f"🤖ChatGPTが長い文を短くします。以下に{INPUT_LIMIT_LENGTH}字未満の文を入力してください。送信する度に結果が変わる可能性があります。"
            )
            style = st.radio(
                "⚠️送信前に元の文体を選んでください。", ("常体（だ・である調）", "敬体（です・ます調）"), horizontal=True
            )
            submit_button = st.form_submit_button(label="ChatGPTに送信")
            if submit_button:
                if len(long_sentence) >= INPUT_LIMIT_LENGTH:
                    st.write(
                        f"入力する文章は{INPUT_LIMIT_LENGTH}字未満にしてください。（現在の文字数：{len(long_sentence)}字）"
                    )
                else:
                    well_written_text = proofread_with_chatgpt.proofreader(
                        long_sentence, style
                    )
                    st.write(f"校正前：{long_sentence}")
                    st.write(f"校正後：{well_written_text}")
