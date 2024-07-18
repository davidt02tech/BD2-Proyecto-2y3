import pandas as pd
import time 
import subprocess
import os
import glob

df = pd.read_csv('spotify_songs.csv')

track_ids = df['track_id'].tolist()[:18000]#[0-999] done [1000-1999] done [2000:2999] done
# [3000-3999] done [4000-4999] done [5000-5999] done
# [6000-6999] done [7000-7999] done
# [8000-8999] done [9000-9999] done
# [10000-10999] done [11000-11999] done
# [12000-12999] done [13000-13999] pending
# [14000-14999] pending [15000-15999] pending


no_existe = ['0T0AY7kzqXBiMuHvI7I3j4', '4ZIvqmpihn94QyFfGcQtdZ', 
             '5BInskLvwqz56ClUpfqdI4', '6l4qV9VNeCOesvcLPJMO9y', 
             '6S9tXDdMzrT8LEk1A8enKF', '74t8ZSV8l9ifqSVZGLyMTv',
             '5uaIbU3oHHcSOK6WFNK5nj']

base_output_dir = "../vector-songs/downloaded"
count = 0

def download_song(track_id, base_output, max_attempts=5):
    url = f'https://open.spotify.com/track/{track_id}'
    attempt = 0
    while attempt < max_attempts:

        command = ['spotdl', 'download', url , '--output', f'{base_output}/{track_id}']
        result = subprocess.run(command, check=True)
        if result.returncode == 0:
            print(f'La canción {track_id} se descargó correctamente')
            return True
        
        attempt += 1
        time.sleep(1)  # Espera un segundo antes de reintentar
    print(f'No se pudo descargar la canción {track_id} después de {max_attempts} intentos.')
    return False

for track_id in track_ids:
    if track_id in no_existe:
        print(f'La canción {track_id} no existe. Omitiendo descarga.')
        continue
    output_dir = os.path.join(base_output_dir, track_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    existing_files = glob.glob(os.path.join(output_dir, '*.mp3'))
    if not existing_files:
        if not download_song(track_id, base_output_dir):
            print(f'Error crítico: No se pudo descargar la canción {track_id}. Terminando el proceso.')
            exit(1)
    else:
        print(f'La canción {track_id} ya existe. Omitiendo descarga.')