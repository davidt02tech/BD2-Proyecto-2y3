from inverted_index import SPIMI


index = SPIMI("spotify_songs.csv",".spimi_data/")
index.build()
