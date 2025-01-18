import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from general import constants as const
from general import log_file_builder as log

logger = log.Logger(const.VOICE_RECORDER_LOGS_FILENAME)


def get_input_channels() -> int:
    try:
        input_device = sd.query_devices(sd.default.device[0], "input")
        channels = input_device.get("max_input_channels", 1)
        logger.log_info(
            f"Detected {channels} channels of default microphone, changing to {min(channels, 2)} input channels.")
        return min(channels, 2)
    except Exception as e:
        logger.log_error(f"Failed to determine input channels: {e}")
        logger.log_info("Changing to default mono channel microphone.")
        return 1


def record_and_save_audio(file_path, duration=5, sample_rate=44100, volume=1.0) -> bool:
    try:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=get_input_channels(),
                            dtype="int16")
        sd.wait()

        audio_data = (volume * audio_data).astype("int16")

        scaled_audio_data = np.int16(audio_data * (32767 / np.max(np.abs(audio_data))))

        write(file_path, sample_rate, scaled_audio_data)

        msg_info = f"Audio {file_path} recorded and saved successfully."
        logger.log_info(msg_info)
        return True

    except Exception as e:
        msg_error = f"Recording or saving audio {file_path} failed. An error occurred: {str(e)}"
        logger.log_error(msg_error)
        return False
