import random
import speech_recognition as sr
import general.constants as const
import logging
from authentication import hash_password


def recognize_speech(audio_file, current_language) -> str:
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        #recognizer.adjust_for_ambient_noise(source, duration=1)

        audio_data = recognizer.record(source)

        try:
            recognized_speech = recognizer.recognize_google(audio_data, language=current_language)
            return str(recognized_speech)
        except sr.UnknownValueError:
            logging.error("Could not understand audio.")
            return ""
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service; {e}")
            return ""


def verify_speaker_nickname(speakers, recognized_speaker_nickname) -> bool:
    if recognized_speaker_nickname.lower() in speakers:
        logging.info("Speaker verified!")
        return True
    else:
        logging.info("Speaker not verified!")
        return False


def verify_verification_word(recognized_verification_word, random_verification_word) -> bool:
    if recognized_verification_word.lower() == random_verification_word.lower():
        logging.info("Verification word verified!")
        return True
    else:
        logging.info("Verification word not verified!")
        return False


def verify_unique_phrase(speakers, logged_user, recognized_unique_phrase) -> bool:
    unique_phrase = list(speakers[logged_user])[0]
    unique_salt = list(speakers[logged_user])[1]
    return hash_password.check_password(recognized_unique_phrase, unique_phrase, unique_salt)



