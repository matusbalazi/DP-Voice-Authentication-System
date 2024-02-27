from general import log_file_builder as log
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np


def record_and_save_audio(file_path, duration=5, sample_rate=44100, volume=1.5) -> bool:
    try:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype="int16")
        sd.wait()

        audio_data = (volume * audio_data).astype("int16")

        scaled_audio_data = np.int16(audio_data * (32767 / np.max(np.abs(audio_data))))

        write(file_path, sample_rate, scaled_audio_data)

        msg_info = f"Audio {file_path} recorded and saved successfully."
        log.log_info(msg_info)
        return True

    except Exception as e:
        msg_error = f"Recording or saving audio {file_path} failed. An error occurred: {str(e)}"
        log.log_error(msg_error)
        return False
