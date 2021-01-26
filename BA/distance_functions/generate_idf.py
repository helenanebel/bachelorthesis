from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import preprocessing
import pandas as pd
import numpy

corpus = [
   'This is the first document.',
   'This document is the second document.',
   'And this is the third one.',
   'Is this the first document?',
    'This is not the first document.'
    ]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)
names = vectorizer.get_feature_names()
idfs = vectorizer.idf_
x = numpy.array(idfs).reshape(-1, 1)
min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
idf_scaled = min_max_scaler.fit_transform(x)
idf_scaled = idf_scaled.flatten()

idf_dict = {name:(idf_scaled[names.index(name)]) for name in names}
print(idf_dict)
# mean idf für gemeinsame Token berechnen!!!
