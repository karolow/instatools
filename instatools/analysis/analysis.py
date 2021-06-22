from collections import Counter
import json
from pathlib import Path
import re

from gensim import corpora
from gensim.models.ldamodel import LdaModel
import pyLDAvis.gensim_models


def generate_lda_viz(hashes, output_file='topics.html', num_topics=5, passes=50):

    dictionary = corpora.Dictionary(hashes)
    corpus = [dictionary.doc2bow(text) for text in hashes]
    ldamodel = LdaModel(corpus,
                        num_topics=num_topics,
                        id2word=dictionary,
                        passes=passes
                        )
    lda_display = pyLDAvis.gensim_models.prepare(ldamodel,
                                                 corpus,
                                                 dictionary,
                                                 sort_topics=True
                                                 )
    pyLDAvis.save_html(lda_display, output_file)
