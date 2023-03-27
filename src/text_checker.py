from module_length import punctuation
import re
import streamlit as st
from annotated_text import annotated_text

if __name__ == "__main__":
    L = []
    with open("hoge.txt", "r") as f:
        text_lists = f.read().splitlines()
        for row_num, text in enumerate(text_lists):
            #sentences = [sentence+"。" for sentence in text.split("。")]  # TODO:ここセリフも句点ついちゃってるのでなんとかする
            sentences = re.split(r"(?<=。)", text)
            for sentence_num, one_sentence in enumerate(sentences):
                if punctuation.find_too_long_sentence(one_sentence):
                    #print(f"長すぎる文章があります：{row_num}行目第{sentence_num+1}文（{len(one_sentence)}文字）")
                    #print(one_sentence)
                    L.append((one_sentence, f"長い（{len(one_sentence)}文字）"))
                else:
                    L.append(one_sentence)
                #if punctuation.find_too_much_punctuation(one_sentence):
                    #print(f"読点が多い文章があります：{row_num}行目第{sentence_num+1}文")
                    #print(one_sentence)
                #if len(punctuation.find_too_less_punctuation(one_sentence)):
                    #print(f"読点を入れるべき文章があります：{row_num}行目第{sentence_num+1}文")
                    #print("該当箇所：")
                    #for part in punctuation.find_too_less_punctuation(one_sentence):
                        #print(part)
            L.append("  \n")  # Streamlitは改行記号の前に半角スペースが2つ必要 (https://github.com/streamlit/streamlit/issues/868)
    annotated_text(*L)
    print(L)
