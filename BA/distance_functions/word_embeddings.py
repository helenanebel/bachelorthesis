import gensim.downloader

# Show all available models in gensim-data

print(list(gensim.downloader.info()['models'].keys()))
glove_vectors = gensim.downloader.load('glove-twitter-25')

# Use the downloaded vectors as usual:

print(glove_vectors.most_similar('twitter'))