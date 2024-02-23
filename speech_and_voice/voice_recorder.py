from general import log_file_builder as log
import sounddevice as sd
import wavio


def record_and_save_audio(file_path, duration=5, sample_rate=44100, volume=1.5) -> bool:
    try:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype="int16")
        sd.wait()

        audio_data = (volume * audio_data).astype("int16")

        wavio.write(file_path, audio_data, sample_rate, sampwidth=3)

        msg_info = f"Audio {file_path} recorded and saved successfully."
        log.log_info(msg_info)
        return True

    except Exception as e:
        msg_error = f"Recording or saving audio {file_path} failed. An error occurred: {str(e)}"
        log.log_error(msg_error)
        return False
