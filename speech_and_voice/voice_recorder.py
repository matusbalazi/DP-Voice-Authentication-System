import sounddevice as sd
import wavio
import logging


def record_and_save_audio(file_path, duration=5, sample_rate=44100, volume=1.5) -> bool:
    try:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype="int16")
        sd.wait()

        audio_data = (volume * audio_data).astype("int16")

        wavio.write(file_path, audio_data, sample_rate, sampwidth=3)

        return True

    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        return False
