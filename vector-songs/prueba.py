import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

# Cargar un archivo de audio
y, sr = librosa.load("../vector-songs/downloaded/0a4agFmqHXxcZl1nho1BxM/Blondie - Heart Of Glass - Special Mix.mp3")

# Calcular el mel espectrograma
S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)

# Convertir el espectrograma a una escala logarítmica (decibelios)
S_dB = librosa.power_to_db(S, ref=np.max)

# Mostrar el mel espectrograma
plt.figure(figsize=(10, 4))
librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel Spectrogram')
plt.tight_layout()
plt.show()

mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

# Mostrar las MFCC
plt.figure(figsize=(10, 4))
librosa.display.specshow(mfccs, sr=sr, x_axis='time')
plt.colorbar()
plt.title('MFCC')
plt.tight_layout()
plt.show()