def overused_expression_checker(sentences, row_num, tokenizer, problematic_parts):
    annotated_text_list = []
    text_position_list = []
    advice_list = []
    problematic_parts = [problematic_part[:2] for problematic_part in problematic_parts]
    for sentence_num, one_sentence in enumerate(sentences):
        tokenized_sentence = tokenizer.tokenize(one_sentence)
        for token in tokenized_sentence:
            if (
                token.part_of_speech.split(",")[0],
                token.base_form,
            ) in problematic_parts:
                annotated_text_list.append((token.surface, "頻発", "#ff3333"))
                text_position_list.append(
                    (f"{row_num+1}行目第{sentence_num+1}文", token.surface)
                )
            else:
                annotated_text_list.append(token.surface)
    return annotated_text_list, text_position_list, advice_list
