import pandas as pd
import json
from dataclasses import dataclass

@dataclass
class Track:
    track_id: str
    track_name: str
    track_artist: str
    lyrics: str
    track_popularity: int
    track_album_id: str
    track_album_name: str
    track_album_release_date: str
    playlist_name: str
    playlist_id: str
    playlist_genre: str
    playlist_subgenre: str
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: int
    language: str

def filtrar_y_obtener_por_track_name(track_name, chunk_size=100):
    csv_file_path = '../src/data/spotify_songs.csv'
    resultados = []

    def filtrar_por_track_name(track_name, dataframe):
        filtered_data = dataframe[dataframe['track_name'] == track_name]
        
        if not filtered_data.empty:
            for _, row in filtered_data.iterrows():
                track = Track(
                    track_id=row['track_id'],
                    track_name=row['track_name'],
                    track_artist=row['track_artist'],
                    lyrics=row['lyrics'],
                    track_popularity=row['track_popularity'],
                    track_album_id=row['track_album_id'],
                    track_album_name=row['track_album_name'],
                    track_album_release_date=row['track_album_release_date'],
                    playlist_name=row['playlist_name'],
                    playlist_id=row['playlist_id'],
                    playlist_genre=row['playlist_genre'],
                    playlist_subgenre=row['playlist_subgenre'],
                    danceability=row['danceability'],
                    energy=row['energy'],
                    key=row['key'],
                    loudness=row['loudness'],
                    mode=row['mode'],
                    speechiness=row['speechiness'],
                    acousticness=row['acousticness'],
                    instrumentalness=row['instrumentalness'],
                    liveness=row['liveness'],
                    valence=row['valence'],
                    tempo=row['tempo'],
                    duration_ms=row['duration_ms'],
                    language=row['language']
                )
                resultados.append(track)

    chunks = pd.read_csv(csv_file_path, chunksize=chunk_size)

    for chunk in chunks:
        filtrar_por_track_name(track_name, chunk)
    
    resultados_dict = [track.__dict__ for track in resultados]
    
    resultados_json = json.dumps(resultados_dict, indent=4)
    
    return resultados_json

# Ejemplo API
nombre_pista = 'Anaconda'
csv_file_path = '../src/data/spotify_songs.csv'
resultados_json = filtrar_y_obtener_por_track_name(nombre_pista)
resultados_lista = json.loads(resultados_json)


print(resultados_lista[0]['track_name'])
print(resultados_lista[0]['track_id'])
