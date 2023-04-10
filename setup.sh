mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
[client]\n\
showErrorDetails = false\n\
" >>~/.streamlit/config.toml

cd data && curl -OL https://github.com/bond-lab/wnja/releases/download/v1.1/wnjpn.db.gz && gzip -d wnjpn.db.gz
curl -OL http://public.shiroyagi.s3.amazonaws.com/latest-ja-word2vec-gensim-model.zip && unzip latest-ja-word2vec-gensim-model.zip && rm latest-ja-word2vec-gensim-model.zip
cd ../