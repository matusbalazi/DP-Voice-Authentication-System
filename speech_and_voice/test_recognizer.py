import torch

import os
import glob

import torchaudio
import torchaudio.transforms as T
from speechbrain.pretrained import EncoderClassifier

import pandas as pd
import numpy as np


def open_audio(audio_signal):
    signal, fs = torchaudio.load(audio_signal)
    resample_rate = 16000
    resampler = T.Resample(fs, resample_rate, dtype=signal.dtype)
    resampled_signal = resampler(signal)
    return resampled_signal


classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir=r"pretrained_models/spkrec-ecapa-voxceleb", run_opts={"device":"cpu"}) #

#vytvori odtlacky hlasu pre recnikov z RAVDESS (10 nahravok)
'''
main_dir = "speaker_recognition/speaker_recordings"
sub_dirs = os.listdir(main_dir)
file_txt = "*.wav"
for sd in sub_dirs:
    try:
        os.mkdir("speaker_recognition/speaker_voiceprints/"+sd)
    except OSError as error:    
        print(error)
    count = 0
    for fn in glob.glob(os.path.join(main_dir, sd, file_txt)):
        print('Current fn:', fn)
        audio_spk = open_audio(fn)
        embedding = classifier.encode_batch(audio_spk)
        torch.save(embedding, "speaker_recognition/speaker_voiceprints/"+sd + '/' + fn.split('\\')[-1].split('.')[0] +'.pt')
        count += 1
        if count == 9:
            break
'''

device = torch.device('cpu')

#nahraj zvukovu nahravku a vytvor odtlacok hlasu
audio_spk2 = open_audio('Matus.wav')
embedding_test = classifier.encode_batch(audio_spk2)

# verify speaker
cos = torch.nn.CosineSimilarity(dim=2, eps=1e-6)

main_dir = "speaker_recognition/speaker_voiceprints"
sub_dirs = os.listdir(main_dir)
df = pd.DataFrame(sub_dirs, columns=['SPK'])
df['score'] = np.zeros(len(sub_dirs))
file_txt = "*.pt"
for sd in sub_dirs:
    for fn in glob.glob(os.path.join(main_dir, sd, file_txt)):
        enroled_utt = torch.load(fn, map_location=device)
        output = cos(enroled_utt, embedding_test)
        if output[0].cpu().detach().numpy() > 0.6:
            df.loc[df['SPK'] == sd, ['score']] += 1

# Using loc[]. Get cell value by index & column name
target = df.loc[df.score == df.score.max()]
target = target['SPK'].values[0]

if (df['score'] == 0).all():
    print("You are not eligible person")
else:
    print('This is speaker ', target)
    print("Open door")


max_score = df['score'].max()
row_with_max_score = df[df['score'] == max_score]
SPK_with_max_score = row_with_max_score['SPK'].values[0]

print("Maximálna hodnota score:", max_score)
print("Prislúchajúci SPK:", SPK_with_max_score)

