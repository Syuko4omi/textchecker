from textchecker.src.module_wordy import wordy_funcs


def test_find_wordy_expression():
    text_1 = "ことができすることができことということという。"
    wordy_expressions_dict = wordy_funcs.create_wordy_expression_dict()
    wordy_parts = wordy_funcs.find_wordy_expression(text_1, wordy_expressions_dict)
    assert wordy_parts == ["ことができ", "することができ", "こと", "ということ", "という"]


def test_wrapper_find_wordy_expression():
    text_1 = "あああすることができあああこと。"
    wordy_expressions_dict = wordy_funcs.create_wordy_expression_dict()
    wordy_expressions, advice_list = wordy_funcs.wrapper_find_wordy_expression(
        text_1, wordy_expressions_dict
    )
    assert wordy_expressions == ["することができ", "こと"]
    assert advice_list == ["代替候補： でき・可能で", "代替候補： -"]


def test_wordy_expression_checker():
    sentences = ["あああ。", "あああすることができあああこと。"]
    wordy_expressions_dict = wordy_funcs.create_wordy_expression_dict()
    (
        annotated_text_list,
        text_position_list,
        advices_list,
    ) = wordy_funcs.wordy_expression_checker(sentences, wordy_expressions_dict, 0)
    assert annotated_text_list == [
        "あああ。",
        "あああ",
        ("することができ", "代替候補： でき・可能で", "#009900"),
        "あああ",
        ("こと", "代替候補： -", "#009900"),
        "。",
    ]
    assert text_position_list == [("1行目第2文", "することができ"), ("1行目第2文", "こと")]
    assert advices_list == ["代替候補： でき・可能で", "代替候補： -"]
