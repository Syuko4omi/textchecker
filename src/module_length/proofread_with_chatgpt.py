import openai
import os
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import SimpleSequentialChain
from module_length import templates


def create_chain(template):  # チェーン（一つの処理の流れ）を作成
    llm = ChatOpenAI()
    template = template
    prompt = HumanMessagePromptTemplate.from_template(template)
    prompt = ChatPromptTemplate.from_messages([prompt])
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain


def proofreader(sentence, style):
    try:  # 環境変数からAPIキーを取得
        openai.api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:  # APIキーが環境変数に設定されていない
        return "ChatGPTを利用するには、OpenAIのAPIキーを設定する必要があります。setやexportコマンドを用いて、環境変数にAPIキーを設定してください。"
    except Exception as e:
        return f"エラーが発生しました。APIの利用制限など様々な原因が考えられます。以下の項目を確認してください\n{e}"

    style_trans_template = (  # 常体敬体テンプレの選択
        templates.keitai_to_jyoutai_template
        if "常体" in style
        else templates.jyoutai_to_keitai_template
    )
    proofread_chain = create_chain(templates.proofread_template)
    style_trans_chain = create_chain(style_trans_template)

    # チェーンを繋げる。校正してから、文体変換を行う
    proofread_and_style_trans_chain = SimpleSequentialChain(
        chains=[proofread_chain, style_trans_chain], verbose=False
    )
    return proofread_and_style_trans_chain.run(sentence)
