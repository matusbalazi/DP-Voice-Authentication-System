import torch
import os
import glob
import pandas as pd
import numpy as np
import torchaudio
import torchaudio.transforms
from general import constants as const
from general import log_file_builder as log

logger = log.Logger(const.VOICE_RECOGNIZER_LOGS_FILENAME)


def open_and_resample_audio_signal(filename, resample_rate=16000):
    allowed_ext = [".wav"]

    if not os.path.isfile(filename):
        msg_error = f"Error: File {filename} does not exist."
        logger.log_error(msg_error)
        return None

    _, ext = os.path.splitext(filename)
    if ext.lower() not in allowed_ext:
        msg_error = f"Error: Unsupported file format {ext.lower()} for resampling audio signal."
        logger.log_error(msg_error)
        return None

    try:
        audio_signal, sample_rate = torchaudio.load(filename)
        resampler = torchaudio.transforms.Resample(sample_rate, resample_rate, dtype=audio_signal.dtype)
        resampled_signal = resampler(audio_signal)
        return resampled_signal
    except Exception as e:
        msg_error = f"Error opening/resampling audio: {e}"
        logger.log_error(msg_error)
        return None


def create_voiceprints(classifier, input_dir, output_dir, num_recordings=10):
    if not os.path.isdir(input_dir):
        msg_error = f"Error: Input directory {input_dir} not found."
        logger.log_error(msg_error)
        return

    file_ext = "*.wav"
    count = 0
    for filename in glob.glob(os.path.join(input_dir, file_ext)):
        speaker_audio_signal = open_and_resample_audio_signal(filename)

        if speaker_audio_signal is not None:
            msg_info = f"Creating voiceprint from audio file {filename}."
            logger.log_info(msg_info)
            voiceprint = classifier.encode_batch(speaker_audio_signal)
            output_voiceprint_file = os.path.join(output_dir, os.path.splitext(os.path.basename(filename))[0] + ".pt")
            try:
                torch.save(voiceprint, output_voiceprint_file)
                count += 1
            except Exception as e:
                msg_error = f"Error saving voiceprint for {filename} to {output_voiceprint_file}: {e}"
                logger.log_error(msg_error)

        if count == num_recordings:
            break


def verify_all_speakers(classifier, input_dir, speaker_audio_path, threshold=0.6):
    speaker_nickname = ""

    if not os.path.isdir(input_dir):
        msg_error = f"Error: Input directory {input_dir} not found."
        logger.log_error(msg_error)
        return speaker_nickname

    device = torch.device("cpu")
    speaker_audio_signal = open_and_resample_audio_signal(speaker_audio_path)

    if speaker_audio_signal is not None:
        voiceprint_test = classifier.encode_batch(speaker_audio_signal)
        cos = torch.nn.CosineSimilarity(dim=2, eps=1e-6)

        input_sub_dirs = os.listdir(input_dir)
        df = pd.DataFrame(input_sub_dirs, columns=["speaker"])
        df["score"] = np.zeros(len(input_sub_dirs))
        file_ext = "*.pt"
        for sub_dir in input_sub_dirs:
            score = 0
            for filename in glob.glob(os.path.join(input_dir, sub_dir, file_ext)):
                enrolled_voiceprint = torch.load(filename, map_location=device)
                result = cos(enrolled_voiceprint, voiceprint_test)

                if result[0].cpu().detach().numpy() > threshold:
                    score += 1
                    df.loc[df["speaker"] == sub_dir, ["score"]] = score

        if (df["score"] == 0).all():
            msg_warning = "Speaker is not an eligible person."
            logger.log_warning(msg_warning)
            speaker_nickname = ""
        else:
            target = df.loc[df.score == df.score.max()]
            target = target["speaker"].values[0]
            msg_info = f"This is authorized speaker {target}."
            logger.log_info(msg_info)
            speaker_nickname = target

        return speaker_nickname


def verify_speaker(classifier, input_dir, speaker_audio_path, threshold=0.6) -> bool:
    success = False

    if not os.path.isdir(input_dir):
        msg_error = f"Error: Input directory {input_dir} not found."
        logger.log_error(msg_error)
        return success

    device = torch.device("cpu")
    speaker_audio_signal = open_and_resample_audio_signal(speaker_audio_path)

    if speaker_audio_signal is not None:
        voiceprint_test = classifier.encode_batch(speaker_audio_signal)
        cos = torch.nn.CosineSimilarity(dim=2, eps=1e-6)

        score = 0
        file_ext = "*.pt"
        for filename in glob.glob(os.path.join(input_dir, file_ext)):
            enrolled_voiceprint = torch.load(filename, map_location=device)
            result = cos(enrolled_voiceprint, voiceprint_test)

            if result[0].cpu().detach().numpy() > threshold:
                score += 1

        if score == 0:
            msg_warning = "Speaker is not an eligible person."
            logger.log_warning(msg_warning)
        else:
            success = True
            msg_info = f"This is an authorized speaker with a score of {score}."
            logger.log_info(msg_info)

    return success


def verify_speaker_concept(classifier, input_dir, speaker_audio_path, threshold=0.5, auth_weight=None) -> tuple:
    success = False
    results = []
    partial_authorization = 0.0

    if not os.path.isdir(input_dir):
        msg_error = f"Error: Input directory {input_dir} not found."
        logger.log_error(msg_error)
        return success, partial_authorization

    device = torch.device("cpu")
    speaker_audio_signal = open_and_resample_audio_signal(speaker_audio_path)

    if speaker_audio_signal is not None:
        voiceprint_test = classifier.encode_batch(speaker_audio_signal)
        cos = torch.nn.CosineSimilarity(dim=2, eps=1e-6)

        score = 0
        file_ext = "*.pt"
        for filename in glob.glob(os.path.join(input_dir, file_ext)):
            enrolled_voiceprint = torch.load(filename, map_location=device)
            result = cos(enrolled_voiceprint, voiceprint_test)
            results.append(round(result[0].cpu().detach().numpy().item(), 2))

            if result[0].cpu().detach().numpy() > threshold:
                score += 1

        if score == 0:
            msg_warning = "Speaker is not an eligible person."
            logger.log_warning(msg_warning)
        else:
            success = True

            partial_authorization = max(results) * 100

            if auth_weight is not None:
                partial_authorization = max(results) * auth_weight

            msg_info = f"This is an authorized speaker with a score of {score}."
            logger.log_info(msg_info)

    return success, partial_authorization

