from textchecker.src.module_length import length_funcs

LENGTH_THRESHOLD = 80
PUNCTUATION_NUM_THRESHOLD = 4
CONTINUOUS_THRESHOLD = 50


def test_find_too_long_sentence(length_threshold=LENGTH_THRESHOLD):
    text_1 = "これは短い文です。"
    text_2 = "あ" * length_threshold
    ret_1 = length_funcs.find_too_long_sentence(text_1)
    ret_2 = length_funcs.find_too_long_sentence(text_2)
    assert ret_1 is False
    assert ret_2 is True


def test_find_too_much_punctuation(punctuation_num_threshold=PUNCTUATION_NUM_THRESHOLD):
    text_1 = "これは短い文です。"
    text_2 = "あ、" * punctuation_num_threshold
    ret_1 = length_funcs.find_too_much_punctuation(text_1)
    ret_2 = length_funcs.find_too_much_punctuation(text_2)
    assert ret_1 is False
    assert ret_2 is True


def test_find_too_less_punctuation(continuous_threshold=CONTINUOUS_THRESHOLD):
    text_1 = "これは短い文です。"
    text_2 = "あ" * continuous_threshold
    ret_1 = length_funcs.find_too_less_punctuation(text_1)
    ret_2 = length_funcs.find_too_less_punctuation(text_2)
    assert ret_1 == []
    assert ret_2 == [text_2]


def test_lengthy_checker():
    sentences = ["これは短い文です。", "あ" * LENGTH_THRESHOLD + "。"]
    annotated_text_list, text_position_list, advice_list = length_funcs.lengthy_checker(
        sentences, row_num=0
    )
    assert annotated_text_list == [
        sentences[0],
        (sentences[1], f"長い（{len(sentences[1])}文字）", "#ff0000"),
    ]
    assert text_position_list == [("1行目第2文", sentences[1])]
    assert advice_list == []


def test_punctuation_num_checker():
    sentences = ["これは短い文です。", "あ、" * PUNCTUATION_NUM_THRESHOLD]
    (
        annotated_text_list,
        text_position_list,
        advice_list,
    ) = length_funcs.punctuation_num_checker(sentences, row_num=0)
    assert annotated_text_list == [
        sentences[0],
        (sentences[1], f"読点が多い（{sentences[1].count('、')}個）", "#ff1a1a"),
    ]
    assert text_position_list == [("1行目第2文", sentences[1])]
    assert advice_list == []


def test_continuous_checker():
    sentences = ["これは短い文です。", "あ" * CONTINUOUS_THRESHOLD + "、あ。"]
    (
        annotated_text_list,
        text_position_list,
        advice_list,
    ) = length_funcs.continuous_checker(sentences, row_num=0)
    assert annotated_text_list == [
        sentences[0],
        (
            "あ" * CONTINUOUS_THRESHOLD + "、",
            f"読点がない（{CONTINUOUS_THRESHOLD+1}文字）",
            "#ff3333",
        ),
        "あ。",
    ]
    assert text_position_list == [("1行目第2文", "あ" * CONTINUOUS_THRESHOLD + "、")]
    assert advice_list == []
