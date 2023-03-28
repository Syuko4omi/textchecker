import json


def create_wordy_expression_dict():
    wordy_expressions = {}
    with open("module_wordy/wordy_expressions.jsonl", "r") as f:
        for line in f:
            instance: dict = json.loads(line)
            wordy_expressions[instance["original_wordy_form"]] = instance[
                "simpler_form"
            ]
    sorted_wordy_expressions = {}
    for key, val in sorted(
        wordy_expressions.items(), key=lambda x: len(x[0]), reverse=True
    ):
        sorted_wordy_expressions[key] = val
    return wordy_expressions


def find_wordy_expression(one_sentence: str, wordy_expressions) -> list[str]:
    wordy_parts = []
    for key in wordy_expressions.keys():
        if len(one_sentence.split(key)) > 1:
            splitted_parts = one_sentence.split(key)
            for idx in range(len(splitted_parts)):
                if idx != len(splitted_parts) - 1:
                    wordy_parts.extend(
                        find_wordy_expression(splitted_parts[idx], wordy_expressions)
                    )
                    wordy_parts.append(key)
                else:
                    wordy_parts.extend(
                        find_wordy_expression(splitted_parts[idx], wordy_expressions)
                    )
            break
    return wordy_parts


def wrapper_find_wordy_expression(one_sentence: str, wordy_expression_dict):
    # まわりくどい言い回しにアラートを出す
    wordy_expressions = find_wordy_expression(one_sentence, wordy_expression_dict)
    advice_list = []
    for wordy_expression in wordy_expressions:
        alternative_expressions = [
            f"「{item}」"
            for item in wordy_expression_dict[wordy_expression]
            if item != ""
        ]
        alt_candidates = "や".join(alternative_expressions)
        if "" in wordy_expression_dict[wordy_expression]:
            if len(wordy_expression_dict[wordy_expression]) == 1:
                advice_list.append("この表現は取り除いても良いと思われます")
            else:
                advice_list.append(f"他の表現（{alt_candidates}）で置き換えるか、取り除くことを検討してみてください")
        else:
            advice_list.append(f"他の表現（{alt_candidates}）で置き換えることを検討してみてください")

    return wordy_expressions
