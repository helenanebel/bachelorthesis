from nltk import ngrams, jaccard_distance
import numpy
import sklearn

s1 = 'Adobe CreativeSuite 5 Master Collection from cheap 4zp'
s2 = 'Adobe CreativeSuite 5 Master Collection from cheap d1x'

s1_trigrams_x = []
s2_trigrams_x = []
trigrams = []
for text in [s1, s2]:
    for i in range(len(text)-2):
        if text == s1:
            s1_trigrams_x.append(text[i:i+3])
        else:
            s2_trigrams_x.append(text[i:i+3])
    trigrams = list(set(s1_trigrams_x + s2_trigrams_x))

s1_trigrams = set(ngrams(s1, n=3))
s2_trigrams = set(ngrams(s2, n=3))

print(1-jaccard_distance(s1_trigrams, s2_trigrams)) # ginge genauso auch mit Worten.

vecs = []
for trigram_set in [s1_trigrams_x, s2_trigrams_x]:
    vec = []
    for trigram in trigrams:
        vec.append(trigram_set.count(trigram))
    vecs.append(vec)

cosine_similarity = min(list(sklearn.metrics.pairwise.cosine_similarity(numpy.array(vecs))[0]))
print(cosine_similarity)

# hier muss noch IDF rein (macht aber für Trigramme nicht sooo viel Sinn.)

