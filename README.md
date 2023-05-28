# textchecker
文章校正ツールです。小説などの校正に利用可能です。  
最大5万字（100KB）くらいまで扱うことができます。（これ以上長い文章も扱えなくはないですが、現実的な時間で校正することが難しいです）

## 動かし方
[pyenv](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)と[poetry](https://python-poetry.org/docs/)が導入されていることを前提とします。（Pythonは3.9.13を使用します）  
以下のコマンドは全てtextcheckerディレクトリで行います。  
最初は以下の1〜4の順に行いますが、二回目以降は「文章校正の実行」のコマンドのみ実行すれば大丈夫です。

### 1. パッケージのインストール
一度行えば十分です。
```
poetry install --no-dev
```

### 2. 日本語WordNet等のダウンロード
一度行えば十分です。1分程度かかります。
```
sh get_resources.sh
```

### 3. コーパスから語彙のidfスコアを計算（スキップ可）
GitHubからクローンしてきた場合、dataディレクトリにlivedoor_corpus_dict.jsonが存在しているはずです。  
その場合、この部分は行わなくても問題ないです。  
8〜10分程度かかります。
```
poetry run python3 src/calculate_idf_score.py
```

### 4. 文章校正の実行
以下のコマンドを実行すると、Streamlitの画面が立ち上がります。  
```
poetry run streamlit run src/text_checker.py
```
ブラウザに以下のような画面が表示されます。

![image](https://user-images.githubusercontent.com/50670279/230769301-caba5e1c-04b4-4530-a53e-14e2ff662968.png)  

校正したいテキストファイルを用意し、画面左上の所定の場所にドラッグ&ドロップするか、Browse filesから好きなファイルを選ぶと、画面上にチェック済みの文章が表示されます。  

終了したい場合は、コマンドラインからCtrl+Cでアプリケーションを終了させ、ブラウザを閉じてください。


## 機能について
現在以下の機能が実装済みです。 
対応しやすいもの、個人的にチェックしてくれると嬉しいものから順に実装しています。

- 長く読み辛い文章
    - 80文字以上の文章
         - ChatGPTを用いて文章を分割する機能があります（後述）
    - 読点が4つ以上使われている文章
    - 読点なしで50文字以上続く部分
- 回りくどい文章
    - 冗長表現
        - 例：〜することができる、〜という
    - 重言
        - 例：違和感を感じる
- 表現に関わるもの
    - 何度も使われる言葉（上位20件）
        - 類語の候補のサジェスト（Wordnet & Word2Vec）
- 体裁に関わるもの
    - 半角英数字
    - 全角英数字
    - 半角カタカナ
    - 半角記号


## ChatGPTを用いた校正について（オプショナル）
### 概要
- 本ツールには[ChatGPT](https://openai.com/blog/chatgpt)を用いた校正機能があります。  
- 想定される利用方法は、まずこのツールで80文字以上の文を見つけ、それをChatGPTに短くしてもらう、という形になります。そのため、入力するのは300字未満の文（句点が一つだけの文章）を想定しています。  

### 使用法
1. まず、サイドバー下部にある入力部に校正したいテキストを入力します。  
2. 次に、元の文章の文体を選択します。常体の「だ・である調」なのか、それとも敬体の「です・ます調」であるのかを、ChatGPT側に教えるのが目的です。  
3. 最後に、サイドバー最下部にある「ChatGPTに送信」ボタンを押し、送信します。通常10秒程度で校正が完了し、結果が表示されます。APIの利用制限上、リクエストを送るのは一分あたり三回程度が望ましいです。

![image](https://github.com/Syuko4omi/textchecker/assets/50670279/d5b0c2b6-e74c-41a4-a76b-7d26b4bc131f)

### APIキーについて
- この機能を利用するには、OpenAIのAPIキーが必要です。
- OpenAIでアカウントを作成してAPIキーを取得したのち、環境変数としてOPENAI_API_KEYという名前で登録すると、この機能が使えるようになります。例えば以下のように~/.bashrcなどに設定してください。
```
export OPENAI_API_KEY=sk-xxx...xxx 
```


## 注意事項
本ツールで検出する事項は、絶対に直さなければならないといったものではありません。  
テキストを機械的に処理しているため、用法などが明らかに妥当な場面でも誤って検出されてしまったり、見当違いなアドバイスをするおそれがあります。  
以上をご理解の上、あくまで参考程度に活用をお願いします。


## 備考
- 「何度も使われる言葉」として検出する単語は、単純に頻度順で見つけているわけではありません。一般的にその言葉がどれくらいよく使われるかと相対的に比較した上で、対象の文章中で多く登場するものをリストアップしています。
    - 「一般的にその言葉がどれくらいよく使われるか」は、[livedoorニュースコーパス](https://www.rondhuit.com/download.html)の全ファイルを元にして計算した[idfスコア](https://ja.wikipedia.org/wiki/Tf-idf)を使用しています。
    - 対象の文書における[tf-idfスコア](https://ja.wikipedia.org/wiki/Tf-idf)が高い方から上位20件を、「よく使われる語彙」としてピックアップして表示しています。
- 「何度も使われる言葉」において表示する関連語は、Word2Vecのコサイン類似度が高い順に並んでいます。
    - ただし、WordNetを元に類義語を探していることで、「犬」の類義語に「スパイ」が挙げられるようなことがあります。また、Word2Vecのコサイン類似度が高い語彙を類義語としているため、「妹」の関連語に「姉」や「母」が挙げられるようなことがあります。
    - 必ずしも類義語ばかりがサジェストされるわけではないことを念頭に置いていただけると幸いです。


## 外部ライブラリ
- [Streamlit](https://streamlit.io)を用いてアプリケーションを実装しています。
- テキストのハイライトには[text-highlighter](https://github.com/kevin91nl/text-highlighter)を使用しています。
- 形態素解析には[Janome](https://mocobeta.github.io/janome/)を使用しています。
- 関連語検索には、[白ヤギコーポレーション](https://shiroyagi.co.jp)が作成した[日本語Word2Vecモデル](https://aial.shiroyagi.co.jp/2017/02/japanese-word2vec-model-builder/)と、[国立研究開発法人情報通信研究機構（NICT）](https://www.nict.go.jp)が整備した[日本語WordNet(1.1)](https://bond-lab.github.io/wnja/jpn/downloads.html)を使用しています。