cd data && curl -OL https://github.com/bond-lab/wnja/releases/download/v1.1/wnjpn.db.gz && gzip -d wnjpn.db.gz
curl -OL http://public.shiroyagi.s3.amazonaws.com/latest-ja-word2vec-gensim-model.zip && unzip latest-ja-word2vec-gensim-model.zip && rm latest-ja-word2vec-gensim-model.zip
# curl -OL https://www.rondhuit.com/downdload/ldcc-20140209.tar.gz && tar -xzvf ldcc-20140209.tar.gz && mv text livedoor_corpus && rm ldcc-20140209.tar.gz
cd ../