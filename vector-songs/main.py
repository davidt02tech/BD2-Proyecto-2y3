import pandas as pd 
import subprocess

df = pd.read_csv('spotify_songs.csv')

track_ids = df['track_id'].tolist()

output_dir = "../vector-songs/downloaded"
count = 2

for track_id in track_ids:
    print(f"id: {count}")
    url = f'https://open.spotify.com/track/{track_id}'
    try:
        command = ['spotdl', 'download', url , '--output', output_dir]
        result = subprocess.run(command, check=True)
        count += 1
    except Exception as e:
        print(f"Failed to download {track_id} due to {e}")

