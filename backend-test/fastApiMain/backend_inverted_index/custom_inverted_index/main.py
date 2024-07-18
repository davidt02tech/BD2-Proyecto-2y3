from inverted_index import SPIMI


index = SPIMI("spotify_songs.csv","indexes/")
index.build()
