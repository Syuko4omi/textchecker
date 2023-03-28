# 一文の長さ、文中の読点の数について見る

"""
def delete_first_and_last_spaces(one_sentence: str) -> str:
    # 文の最初と最後のスペース類を消す
    stripped_sentence = one_sentence.strip()
    return stripped_sentence
"""


def find_too_long_sentence(one_sentence: str) -> bool:
    # 一文が80文字以上の文章にはアラートを出す
    # one_sentence = delete_first_and_last_spaces(one_sentence)
    if len(one_sentence) >= 80:
        return True
    else:
        return False


def find_too_much_punctuation(one_sentence: str) -> bool:
    # 文中に読点が4つ以上あったら、その文にアラートを出す
    if one_sentence.count("、") >= 4:
        return True
    else:
        return False


def find_too_less_punctuation(one_sentence: str) -> list[str]:
    # 読点抜きで50文字以上連続する部分にはアラートを出す
    too_less_punctuation_parts = []
    # one_sentence = delete_first_and_last_spaces(one_sentence)
    parts = one_sentence.split("、")
    for part in parts:
        if len(part) >= 50:
            too_less_punctuation_parts.append(part)
    return too_less_punctuation_parts
