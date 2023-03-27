# textchecker

## 動かし方
```
poetry run streamlit run text_checker.py
```

## 機能について
以下の4つについてチェックします。
- 長く読み辛い文章
    - hoge
- 回りくどい文章
    - 冗長表現
    - 重言
- 体裁に関わるもの
    - 全角になっていない英数字
    - 半角カタカナ
    - 常体・敬体の乱れ
- 表現に関わるもの
    - 何度も使われる言葉
        - 可能であれば、ここで類語の候補をサジェストしたい
    - ワンパターンな文末の表現

### ライブラリ
テキストのハイライトには[text-highlighter](https://github.com/kevin91nl/text-highlighter)を使用しています。