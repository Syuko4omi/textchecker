import unicodedata
import re
from janome.tokenizer import Tokenizer
from module_expression.config import POS_LIST


def text_preprocessor(text: str) -> str:
    # 全角・半角の表記を揃えたり、数字などがidfスコアの辞書で登録されるのを避けたりする
    text = unicodedata.normalize("NFKC", text)  # NFKC正規化
    text = re.sub(r"\d+", "0", text)  # 数字を0に置換
    return text


def create_base_form_list(
    tokenizer, texts: list[str], pos_option=None
) -> list[list[str]]:
    # 一つの文章の中から、pos_listにある品詞がついた語だけを取り出し、それを語幹として返す（重複あり）
    # 語幹に対するidfスコアを計算するための前処理として行う
    # find_overused_word.pyでは、pos_optionで品詞のリストを指定すれば、それに絞って探すことができる
    base_form_list = []
    pos_list = POS_LIST if pos_option is None else pos_option
    for text in texts:
        text = text_preprocessor(text)
        for token in tokenizer.tokenize(text):
            if token.part_of_speech.split(",")[0] in pos_list:
                base_form_list.append(
                    [token.part_of_speech.split(",")[0], token.base_form]  # 品詞と語幹
                )
    return base_form_list


def prepare_tokenizer():
    # 半角記号が「名詞,サ変接続」と認識されてしまうので、これを「記号,一般」にする
    # 詳しくはhttps://qiita.com/sentencebird/items/60ee3337ed96478eb217
    tokenizer = Tokenizer()
    symbol_settings = list(tokenizer.sys_dic.unknowns["SYMBOL"][0])
    symbol_settings[3] = "記号,一般,*,*"
    tokenizer.sys_dic.unknowns["SYMBOL"][0] = symbol_settings

    return tokenizer


def dict_add_append(my_dict, key):
    if key in my_dict:
        my_dict[key] += 1
    else:
        my_dict[key] = 1
    return my_dict


def merge_parts(L):
    # パーツが多くなるとannotated_textsが重くなるので、バラバラになったものを適度にまとめる（以下の例を参照）
    # ["hoge", "fuga", ("hogehoge", 2), "pohe"] -> ['hogefuga', ('hogehoge', 2), 'pohe']
    buf = ""
    ret = []
    for i in range(len(L)):
        if str(L[i]) == L[i]:
            buf += L[i]
        else:
            ret.append(buf)
            ret.append(L[i])
            buf = ""
    if buf != "":
        ret.append(buf)
    return ret
