import random
import speech_recognition as sr
from authentication import string_hasher
from general import constants as const
from general import log_file_builder as log

logger = log.Logger(const.SPEECH_RECOGNIZER_LOGS_FILENAME)


def recognize_speech(audio_file, current_language) -> str:
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        # recognizer.adjust_for_ambient_noise(source, duration=1)

        audio_data = recognizer.record(source)

        try:
            recognized_speech = recognizer.recognize_google(audio_data, language=current_language)
            return str(recognized_speech)
        except sr.UnknownValueError:
            msg_error = "Could not understand audio."
            logger.log_error(msg_error)
            return ""
        except sr.RequestError as e:
            msg_error = f"Could not request results from Google Speech Recognition service; {str(e)}"
            logger.log_error(msg_error)
            return ""


def verify_speaker_nickname(speakers, recognized_speaker_nickname) -> bool:
    if recognized_speaker_nickname.lower() in speakers:
        logger.log_info("Speaker verified!")
        return True
    else:
        logger.log_warning("Speaker not verified!")
        return False


def verify_verification_word(recognized_verification_word, random_verification_word) -> bool:
    if recognized_verification_word.lower() == random_verification_word.lower():
        logger.log_info("Verification word verified!")
        return True
    else:
        logger.log_warning("Verification word not verified!")
        return False


def verify_unique_phrase(speakers, logged_user, recognized_unique_phrase) -> bool:
    success = False

    if logged_user != "":
        unique_phrase = list(speakers[logged_user])[0]
        unique_salt = list(speakers[logged_user])[1]
        success = string_hasher.check_string(recognized_unique_phrase, unique_phrase, unique_salt)
    else:
        for values in speakers.values():
            phrase = list(values)[0]
            salt = list(values)[1]
            success = string_hasher.check_string(recognized_unique_phrase, phrase, salt)
            if success:
                break

    if success:
        logger.log_info("Unique phrase verified!")
        return True
    else:
        logger.log_warning("Unique phrase not verified!")
        return False


def generate_random_word(set_of_words) -> str:
    random_verification_word = random.choice(set_of_words)
    return random_verification_word


def find_user_nickname(users, recognized_unique_phrase) -> str:
    user_nickname = ""

    for key, value in users.items():
        if string_hasher.check_string(recognized_unique_phrase, value[0], value[1]):
            user_nickname = key
            break

    return user_nickname


def user_registered_with_internet(users, recognized_speaker_nickname) -> bool:
    return list(users[recognized_speaker_nickname])[2]
