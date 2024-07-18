import pandas as pd
import time 
import subprocess
import os
import glob
import numpy as np
import librosa

df = pd.read_csv('spotify_songs.csv')
features_csv = 'song_features.csv'
missing_files_txt = 'missing_files.txt'

track_ids = df['track_id'].tolist()
mfcc_coeff = 13

def extract_features(file_path, n=13):
    y, sr = librosa.load(file_path)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n)
    
    features = {
        'mean': np.mean(mfccs, axis=1),
        'std': np.std(mfccs, axis=1),
        'median': np.median(mfccs, axis=1),
        'q25': np.percentile(mfccs, 25, axis=1),
        'q75': np.percentile(mfccs, 75, axis=1),
        'min': np.min(mfccs, axis=1),
        'max': np.max(mfccs, axis=1)
    }
    
    combined_features = np.concatenate([
        features['mean'], features['std'], features['median'], 
        features['q25'], features['q75'], features['min'], features['max']
    ])
    
    return combined_features

if os.path.exists(features_csv):
    existing_df = pd.read_csv(features_csv)
else:
    columns = ['track_id'] + list(range(13 * 7))  # 7 estadísticas para cada uno de los 13 coeficientes MFCC
    existing_df = pd.DataFrame(columns=columns)

new_results = []
base_output_dir = "../vector-songs/downloaded"


with open(missing_files_txt, 'a') as missing_file:
    for track_id in track_ids:
        output_dir = os.path.join(base_output_dir, track_id)
        audio_files = glob.glob(os.path.join(output_dir, '*.mp3'))
        if audio_files:
            file_path = audio_files[0]
            try:
                features = extract_features(file_path)
                # print(features)
                features_row = [track_id] + features.tolist()
                new_results.append(features_row)
                print(f'Características extraídas para {track_id}.')
            except Exception as e:
                print(f'Error al extraer características de {track_id}: {e}')
        else:
            print(f'Archivo no encontrado para {track_id}.')
            missing_file.write(f'{track_id}\n')

new_features_df = pd.DataFrame(new_results, columns=existing_df.columns)

combined_df = pd.concat([existing_df, new_features_df]).drop_duplicates(subset=['track_id'], keep='last')

combined_df.to_csv(features_csv, index=False)
print('Características de las canciones guardadas en', features_csv)



# # lectura por índice
# df1 = pd.read_csv('song_features.csv')
# track_features = df1.iloc[0].tolist()[1:]
# print(track_features)

# # lectura por track_id
# df1 = pd.read_csv('song_features.csv')
# track_features = df1.loc[df1['track_id'] == '00NAQYOP4AmWR549nnYJZu']
# result = track_features.iloc[0,1:].tolist()
# print(result)