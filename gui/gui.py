import os
import time
import customtkinter as ctk
import tkinter as tk

from speechbrain.pretrained import EncoderClassifier
from translations import Translations
from authentication import credentials, string_hasher
from general import constants as const
from general import log_file_builder as log
from general import file_manager as manager
from speech_and_voice import voice_recorder as recorder
from speech_and_voice import speech_recognizer as s_recognizer
from speech_and_voice import voice_recognizer as v_recognizer
from database import json_file_builder as json
from database import connection_controller as conn

user_to_delete = ""
currently_logged_user = ""
new_user_nickname = ""
new_user_unique_phrase = ""

remaining_attempts = 3
voiceprints_counter = 0
recordings_counter = 0

ctk.set_ctk_parent_class(tk.Tk)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

window = ctk.CTk()

width = window.winfo_screenwidth()
height = window.winfo_screenheight()

window.geometry("%dx%d+0+0" % (width, height))
window.attributes("-fullscreen", True)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


def create_frame():
    frame = ctk.CTkFrame(master=window)
    frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    for i in range(9):
        frame.columnconfigure(i, weight=1)
        frame.rowconfigure(i, weight=1)

    return frame


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def clear_frames(frames):
    for frame in frames:
        for widget in frame.winfo_children():
            widget.destroy()


def clear_global_variables():
    global user_to_delete, currently_logged_user, new_user_nickname, new_user_unique_phrase, remaining_attempts, voiceprints_counter
    user_to_delete = ""
    currently_logged_user = ""
    new_user_nickname = ""
    new_user_unique_phrase = ""
    remaining_attempts = 3
    voiceprints_counter = 0


def change_language(language):
    Translations.set_language(language)
    update_translations()


def update_translations():
    label_main_title.configure(text=Translations.get_translation('system_authentication'))
    button_open_door.configure(text=Translations.get_translation('open_door'))
    button_about_project.configure(text=Translations.get_translation('about_project'))
    button_exit.configure(text=Translations.get_translation('exit'))


# create OPEN DOOR FRAME widgets
def button_open_door_callback():
    frame_intro.lower()
    frame_open_door.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_open_door, text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('exit'),
                                font=("Roboto", 38, "bold"),
                                command=button_exit_callback, width=150, height=50)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_open_door, frame_intro), width=150,
                                height=50)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_sign_in = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_in'),
                                   font=("Roboto", 48, "bold"), command=button_sign_in_callback)
    button_sign_in.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_sign_up = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_up'),
                                   font=("Roboto", 48, "bold"), command=button_sign_up_callback)
    button_sign_up.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")


# create ABOUT FRAME widgets
def button_about_project_callback():
    frame_intro.lower()
    frame_about.lift()

    label_main_title = ctk.CTkLabel(master=frame_about, text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_about, text=Translations.get_translation('exit'),
                                font=("Roboto", 38, "bold"),
                                command=button_exit_callback, width=150, height=100)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_about, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_about, frame_intro), width=150, height=100)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    label_thesis = ctk.CTkLabel(master=frame_about, text=Translations.get_translation('thesis'),
                                font=("Roboto", 42, "bold"), justify=ctk.CENTER)
    label_thesis.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    label_about_project = ctk.CTkLabel(master=frame_about,
                                       text=Translations.get_translation('topic') + "\n" + Translations.get_translation(
                                           'student') + "\n" + Translations.get_translation(
                                           'mentor') + "\n" + Translations.get_translation('year'),
                                       font=("Roboto", 32), justify=ctk.LEFT)
    label_about_project.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_school = ctk.CTkLabel(master=frame_about, text=(
            Translations.get_translation('university') + "\n\n" + Translations.get_translation(
        'faculty') + "\n\n" + Translations.get_translation('department')), font=("Roboto", 32),
                                justify=ctk.CENTER)
    label_school.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")

    entry_password = ctk.CTkEntry(master=frame_about, font=("Roboto", 38, "bold"), placeholder_text="", show="*",
                                  justify=ctk.CENTER, width=150, height=100)
    entry_password.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_password = ctk.CTkButton(master=frame_about, text=Translations.get_translation('confirm'),
                                    font=("Roboto", 38, "bold"),
                                    command=lambda: button_password_callback(entry_password.get()), width=150,
                                    height=100)
    button_password.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_exit_callback():
    window.destroy()


def segmented_button_language_callback(value):
    change_language(value)


def button_back_callback(frame_to_hide, frame_to_show):
    global voiceprints_counter
    voiceprints_counter = 0
    clear_frame(frame_to_hide)
    frame_to_hide.lower()
    frame_to_show.lift()


def button_password_callback(value):
    correct_password = string_hasher.check_string(value, credentials.password, credentials.sol)
    if correct_password:
        if conn.check_internet_connection():
            frame_about.lower()
        else:
            frame_not_internet_connection.lower()

        frame_authentication_phase_3_callback()
        msg_success = "Entered password was correct."
        log.log_info(msg_success)
    else:
        msg_warning = "Entered password was incorrect."
        log.log_warning(msg_warning)


# create AUTHENTICATION PHASE 1 FRAME widgets -> after click on SIGN IN button
def button_sign_in_callback():
    frame_open_door.lower()

    if conn.check_internet_connection():
        frame_authentication_phase_1.lift()
        clear_frames(authentication_frames)

        label_main_title = ctk.CTkLabel(master=frame_authentication_phase_1,
                                        text=Translations.get_translation('system_authentication'),
                                        font=("Roboto", 48, "bold"), justify=ctk.CENTER)
        label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

        label_first_phase = ctk.CTkLabel(master=frame_authentication_phase_1,
                                         text=Translations.get_translation('first_phase'),
                                         font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
        label_first_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

        label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_1,
                                               text=Translations.get_translation(
                                                   'come_closer_1') + "\n\n" + Translations.get_translation(
                                                   'start_recording'),
                                               font=("Roboto", 38), justify=ctk.LEFT)
        label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

        button_back = ctk.CTkButton(master=frame_authentication_phase_1, text=Translations.get_translation('back'),
                                    font=("Roboto", 38, "bold"),
                                    command=lambda: button_back_callback(frame_authentication_phase_1, frame_open_door),
                                    width=275,
                                    height=70)
        button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

        button_authenticate = ctk.CTkButton(master=frame_authentication_phase_1,
                                            text=Translations.get_translation('authenticate'),
                                            font=("Roboto", 38, "bold"),
                                            command=lambda: button_authenticate_phase_1_callback(label_first_phase,
                                                                                                 label_authenticate_user,
                                                                                                 button_back,
                                                                                                 button_authenticate),
                                            width=275,
                                            height=70)
        button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

        window.update()
    else:
        frame_not_internet_connection_callback()


def frame_not_internet_connection_callback():
    frame_not_internet_connection.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_not_internet_connection,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_not_connection = ctk.CTkLabel(master=frame_not_internet_connection,
                                     text=Translations.get_translation('internet'),
                                     font=("Roboto", 38, "bold"), text_color="red", justify=ctk.CENTER)
    label_not_connection.grid(row=3, column=4, sticky="nsew")

    label_limited_mode = ctk.CTkLabel(master=frame_not_internet_connection,
                                           text=Translations.get_translation(
                                               'limited_mode') + "\n\n" + Translations.get_translation(
                                               'password_to_continue'),
                                           font=("Roboto", 38), justify=ctk.LEFT)
    label_limited_mode.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_not_internet_connection, text=Translations.get_translation('exit'),
                                font=("Roboto", 38, "bold"),
                                command=button_exit_callback, width=150, height=60)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_not_internet_connection, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_not_internet_connection, frame_open_door), width=150, height=60)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    entry_password = ctk.CTkEntry(master=frame_not_internet_connection, font=("Roboto", 38, "bold"), placeholder_text="", show="*",
                                  justify=ctk.CENTER, width=150, height=60)
    entry_password.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_password = ctk.CTkButton(master=frame_not_internet_connection, text=Translations.get_translation('confirm'),
                                    font=("Roboto", 38, "bold"),
                                    command=lambda: button_password_callback(entry_password.get()), width=150,
                                    height=60)
    button_password.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_authenticate_phase_1_callback(label_first_phase, label_authenticate_user, button_back, button_authenticate):
    global currently_logged_user

    label_first_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()

    internet_available = True
    timeout = 10
    start_time = time.time()
    while not conn.check_internet_connection():
        label_authenticate_user.configure(text=Translations.get_translation('waiting_for_connection'))
        window.update()
        if time.time() - start_time >= timeout:
            frame_not_internet_connection_callback()
            internet_available = False
            break

    if internet_available:
        label_authenticate_user.configure(text=Translations.get_translation('recording'))
        window.update()

        # SPEECH RECOGNITION
        recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
        speaker_nickname = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME, Translations.get_language().lower())
        speaker_nickname = speaker_nickname.lower()
        speaker_exists = s_recognizer.verify_speaker_nickname(users.keys(), speaker_nickname)

        msg_info = f"Recognized speaker nickname: {speaker_nickname}"
        log.log_info(msg_info)

        label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
        window.update()

        time.sleep(1.5)

        if speaker_exists:
            currently_logged_user = speaker_nickname.lower()

            speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + speaker_nickname + "/"
            login_success = v_recognizer.verify_speaker(classifier, speaker_dir, const.RECORDED_AUDIO_FILENAME)

            if login_success:
                msg_success = f"User {speaker_nickname} signed in successfully."
                log.log_info(msg_success)
                frame_authentication_phase_2_callback()
            else:
                msg_warning = f"User {speaker_nickname} failed to sign in. Voice characteristics don't match."
                log.log_warning(msg_warning)
                frame_authentication_unsuccess_callback(1)
        else:
            msg_warning = f"Speaker {speaker_nickname} does not exist. "
            log.log_warning(msg_warning)
            frame_authentication_unsuccess_callback(1)


# create AUTHENTICATION PHASE 2 FRAME widgets
def frame_authentication_phase_2_callback():
    frame_authentication_phase_1.lower()
    frame_authentication_phase_2.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_authentication_phase_2,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_sign_in_success = ctk.CTkLabel(master=frame_authentication_phase_2,
                                         text=Translations.get_translation('sign_in_success'),
                                         font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_sign_in_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    time.sleep(1.5)

    label_sign_in_success.destroy()

    label_second_phase = ctk.CTkLabel(master=frame_authentication_phase_2,
                                      text=Translations.get_translation('second_phase'),
                                      font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_second_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_2,
                                           text=Translations.get_translation(
                                               'come_closer_2') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=("Roboto", 38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_authentication_phase_2, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_authentication_phase_2, frame_open_door),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_authentication_phase_2,
                                        text=Translations.get_translation('authenticate'),
                                        font=("Roboto", 38, "bold"),
                                        command=lambda: button_authenticate_phase_2_callback(label_second_phase,
                                                                                             label_authenticate_user,
                                                                                             button_back,
                                                                                             button_authenticate),
                                        width=275,
                                        height=70)
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    window.update()


def button_authenticate_phase_2_callback(label_second_phase, label_authenticate_user, button_back, button_authenticate):
    label_second_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()

    internet_available = True
    timeout = 10
    start_time = time.time()
    while not conn.check_internet_connection():
        label_authenticate_user.configure(text=Translations.get_translation('waiting_for_connection'))
        window.update()
        if time.time() - start_time >= timeout:
            frame_not_internet_connection_callback()
            internet_available = False
            break

    if internet_available:
        random_word = s_recognizer.generate_random_word(const.VERIFICATION_WORDS[Translations.get_language()])

        label_random_word = ctk.CTkLabel(master=frame_authentication_phase_2,
                                         text=random_word.upper(),
                                         font=("Roboto", 48, "bold"), text_color=("light green"), justify=ctk.CENTER)
        label_random_word.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

        label_authenticate_user.configure(text=Translations.get_translation('recording'))
        window.update()

        # SPEECH RECOGNITION
        recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
        spoken_verification_word = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                                 Translations.get_language().lower())
        spoken_verification_word_matches = s_recognizer.verify_verification_word(spoken_verification_word, random_word)

        msg_info = f"Recognized verification word: {spoken_verification_word}"
        log.log_info(msg_info)

        label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
        window.update()

        time.sleep(1.5)

        if spoken_verification_word_matches:
            speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + currently_logged_user + "/"
            verification_success = v_recognizer.verify_speaker(classifier, speaker_dir, const.RECORDED_AUDIO_FILENAME)

            if verification_success:
                msg_success = f"Verification word {random_word} matched with spoken word {spoken_verification_word}. Speaker is registered user."
                log.log_info(msg_success)
                frame_authentication_phase_3_callback()
            else:
                msg_warning = f"Speaker's voice characteristics don't match."
                log.log_warning(msg_warning)
                frame_authentication_unsuccess_callback(2)
        else:
            msg_warning = f"Verification word {random_word} didn't match with spoken word {spoken_verification_word}."
            log.log_warning(msg_warning)
            frame_authentication_unsuccess_callback(2)


# create AUTHENTICATION PHASE 3 FRAME widgets
def frame_authentication_phase_3_callback():
    frame_authentication_phase_2.lower()
    frame_authentication_phase_3.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_authentication_phase_3,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_verification_success = ctk.CTkLabel(master=frame_authentication_phase_3,
                                              text=Translations.get_translation('verification_success'),
                                              font=("Roboto", 38, "bold"), text_color=("light green"),
                                              justify=ctk.CENTER)
    label_verification_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    time.sleep(1.5)

    label_verification_success.destroy()

    label_third_phase = ctk.CTkLabel(master=frame_authentication_phase_3,
                                     text=Translations.get_translation('third_phase'),
                                     font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_third_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_3,
                                           text=Translations.get_translation(
                                               'come_closer_3') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=("Roboto", 38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_authentication_phase_3, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_authentication_phase_3, frame_open_door),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_authentication_phase_3,
                                        text=Translations.get_translation('authenticate'),
                                        font=("Roboto", 38, "bold"),
                                        command=lambda: button_authenticate_phase_3_callback(label_third_phase,
                                                                                             label_authenticate_user,
                                                                                             button_back,
                                                                                             button_authenticate),
                                        width=275,
                                        height=70)
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    window.update()


def button_authenticate_phase_3_callback(label_third_phase, label_authenticate_user, button_back, button_authenticate):
    global currently_logged_user

    label_third_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()
    label_authenticate_user.configure(text=Translations.get_translation('recording'))
    window.update()

    recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)

    if conn.check_internet_connection():
        unique_phrase = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                      Translations.get_language().lower())
        unique_phrase = unique_phrase.lower()
        unique_phrase_matches = s_recognizer.verify_unique_phrase(users, currently_logged_user, unique_phrase)
    else:
        unique_phrase = ""
        unique_phrase_matches = True

    label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()

    time.sleep(1.5)

    if unique_phrase_matches:
        if currently_logged_user == "":
            currently_logged_user = v_recognizer.verify_all_speakers(classifier, const.SPEAKER_VOICEPRINTS_DIR,
                                                                     const.RECORDED_AUDIO_FILENAME)

            if unique_phrase != "":
                if not s_recognizer.verify_unique_phrase(users, currently_logged_user, unique_phrase):
                    currently_logged_user = ""

        if currently_logged_user != "":
            speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + currently_logged_user + "/"
            authentication_success = v_recognizer.verify_speaker(classifier, speaker_dir,
                                                                 const.RECORDED_AUDIO_FILENAME)

            if authentication_success:
                msg_success = f"Authentication with unique phrase was successful. User {currently_logged_user} opened the door."
                log.log_info(msg_success)
                if os.path.isfile(const.RECORDED_AUDIO_FILENAME):
                    os.remove(const.RECORDED_AUDIO_FILENAME)
                frame_authentication_success_callback()
            else:
                msg_warning = f"Speaker's voice characteristics don't match. Door can't be opened."
                log.log_warning(msg_warning)
                frame_authentication_unsuccess_callback(3)
        else:
            msg_warning = f"Speaker's voice characteristics don't correspond with his unique phrase."
            log.log_warning(msg_warning)
            frame_authentication_unsuccess_callback(3)
    else:
        msg_warning = f"Authentication with unique phrase wasn't successful. User {currently_logged_user} couldn't open the door."
        log.log_warning(msg_warning)
        frame_authentication_unsuccess_callback(3)


# create AUTHENTICATION SUCCESS FRAME widgets
def frame_authentication_success_callback():
    global remaining_attempts
    remaining_attempts = 3

    clear_frame(frame_authentication_success)
    frame_authentication_phase_3.lower()
    frame_authentication_success.lift()

    label_main_title = ctk.CTkLabel(master=frame_authentication_success,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_authentication_success = ctk.CTkLabel(master=frame_authentication_success,
                                                text=Translations.get_translation('authentication_success'),
                                                font=("Roboto", 38, "bold"), text_color=("light green"),
                                                justify=ctk.CENTER)
    label_authentication_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    time.sleep(1.5)

    label_authentication_success.destroy()

    label_logged_user = ctk.CTkLabel(master=frame_authentication_success,
                                     text=Translations.get_translation('logged_user') + currently_logged_user,
                                     font=("Roboto", 38, "bold"), text_color="light green", justify=ctk.CENTER)
    label_logged_user.grid(row=2, column=4, sticky="nsew")

    button_end_interaction = ctk.CTkButton(master=frame_authentication_success,
                                           text=Translations.get_translation('end_interaction'),
                                           font=("Roboto", 48, "bold"), command=button_end_interaction_callback)
    button_end_interaction.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_register_user = ctk.CTkButton(master=frame_authentication_success,
                                         text=Translations.get_translation('register_user'),
                                         font=("Roboto", 48, "bold"), command=button_register_user_callback)
    button_register_user.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")

    if const.IS_ADMIN and conn.check_internet_connection():
        button_manage_users = ctk.CTkButton(master=frame_authentication_success,
                                            text=Translations.get_translation('manage_users'),
                                            font=("Roboto", 48, "bold"), command=button_manage_users_callback)
        button_manage_users.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")


def button_end_interaction_callback():
    frame_authentication_success.lower()
    clear_frame(frame_authentication_success)
    clear_global_variables()
    frame_intro.lift()


# create AUTHENTICATION UNSUCCESS FRAME widgets
def frame_authentication_unsuccess_callback(phase):
    global remaining_attempts
    remaining_attempts -= 1

    msg_warning = f"Error during authentication process. Remaining attempts: {remaining_attempts}"
    log.log_warning(msg_warning)

    if phase == 1:
        frame_authentication_phase_1.lower()
    elif phase == 2:
        frame_authentication_phase_2.lower()
    elif phase == 3:
        frame_authentication_phase_3.lower()
    else:
        pass

    if remaining_attempts == 0:
        remaining_attempts = 3
        frame_intro.lift()
    else:
        frame_authentication_unsuccess.lift()

    label_main_title = ctk.CTkLabel(master=frame_authentication_unsuccess,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_authentication_unsuccess = ctk.CTkLabel(master=frame_authentication_unsuccess,
                                                  text=Translations.get_translation('authentication_unsuccess'),
                                                  font=("Roboto", 38, "bold"), text_color=("red"), justify=ctk.CENTER)
    label_authentication_unsuccess.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_authentication_unsuccess_info = ctk.CTkLabel(master=frame_authentication_unsuccess,
                                                       text=Translations.get_translation(
                                                           'authentication_unsuccess_info') + "\n\n" + Translations.get_translation(
                                                           'remaining_attempts') + str(
                                                           remaining_attempts) + "\n\n" + Translations.get_translation(
                                                           'start_authentication_again'),
                                                       font=("Roboto", 38), justify=ctk.LEFT)
    label_authentication_unsuccess_info.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_authenticate_again = ctk.CTkButton(master=frame_authentication_unsuccess,
                                              text=Translations.get_translation('authenticate_again'),
                                              font=("Roboto", 48, "bold"),
                                              command=lambda: button_authenticate_again_callback(phase),
                                              width=150,
                                              height=100)
    button_authenticate_again.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_authenticate_again_callback(phase):
    frame_authentication_unsuccess.lower()

    if phase == 1:
        button_sign_in_callback()
    elif phase == 2:
        frame_authentication_phase_2_callback()
    elif phase == 3:
        frame_authentication_phase_3_callback()
    else:
        pass


# create REGISTRATION FRAME widgets
def button_sign_up_callback():
    frame_open_door.lower()
    frame_registraction.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_registraction,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_registration = ctk.CTkLabel(master=frame_registraction,
                                      text=Translations.get_translation(
                                          'registration_info') + "\n\n" + Translations.get_translation(
                                          'continue_to_sign_in'),
                                      font=("Roboto", 38), justify=ctk.LEFT)
    label_registration.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    button_sign_in_again = ctk.CTkButton(master=frame_registraction, text=Translations.get_translation('sign_in'),
                                         font=("Roboto", 48, "bold"), command=button_sign_in_callback)
    button_sign_in_again.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")


# create REGISTER NEW USER FRAME widgets
def button_register_user_callback():
    frame_authentication_success.lower()
    frame_register_new_user.lift()
    clear_frames(registration_frames)

    label_main_title = ctk.CTkLabel(master=frame_register_new_user,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_first_phase = ctk.CTkLabel(master=frame_register_new_user,
                                     text=Translations.get_translation('registration_first_phase'),
                                     font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_first_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_register_user = ctk.CTkLabel(master=frame_register_new_user,
                                       text=Translations.get_translation(
                                           'register_come_closer_1') + "\n\n" + Translations.get_translation(
                                           'register_start_recording'),
                                       font=("Roboto", 38), justify=ctk.LEFT)
    label_register_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_register_new_user, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_register_new_user,
                                                                     frame_authentication_success),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_registrate = ctk.CTkButton(master=frame_register_new_user,
                                      text=Translations.get_translation('registrate'),
                                      font=("Roboto", 38, "bold"),
                                      command=lambda: button_registrate_phase_1_callback(label_first_phase,
                                                                                         label_register_user,
                                                                                         button_back,
                                                                                         button_registrate),
                                      width=275,
                                      height=70)
    button_registrate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")


def button_registrate_phase_1_callback(label_first_phase, label_register_user, button_back, button_registrate):
    global new_user_nickname

    label_first_phase.destroy()
    label_register_user.configure(text=Translations.get_translation('recording'))
    button_back.destroy()
    button_registrate.destroy()
    window.update()

    # SPEECH recognition
    recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
    new_user_nickname = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                      Translations.get_language().lower())
    new_user_nickname = new_user_nickname.lower()

    msg_info = f"Recognized new user nickname: {new_user_nickname}"
    log.log_info(msg_info)

    label_register_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()

    time.sleep(1.5)

    label_register_user.configure(text=Translations.get_translation('confirmation_nickname') + new_user_nickname)

    button_repeat = ctk.CTkButton(master=frame_register_new_user, text=Translations.get_translation('repeat'),
                                  font=("Roboto", 38, "bold"),
                                  command=button_repeat_phase_1_callback,
                                  width=275,
                                  height=70)
    button_repeat.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_confirm = ctk.CTkButton(master=frame_register_new_user,
                                   text=Translations.get_translation('confirm'),
                                   font=("Roboto", 38, "bold"),
                                   command=button_confirm_phase_1_callback,
                                   width=275,
                                   height=70, state="normal")
    button_confirm.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    if new_user_nickname in users:
        button_confirm.configure(state="disabled")
        label_register_user.configure(
            text=Translations.get_translation('nickname_exists_1') + new_user_nickname + Translations.get_translation(
                'nickname_exists_2') + "\n\n" + Translations.get_translation('nickname_exists_3'),
            font=("Roboto", 38, "bold"), text_color="red")

    window.update()


def button_repeat_phase_1_callback():
    button_register_user_callback()


# create REGISTER NEW VOICEPRINTS FRAME widgets
def button_confirm_phase_1_callback():
    global new_user_nickname, voiceprints_counter, recordings_counter

    if voiceprints_counter == 0:
        msg_info = f"New user nickname {new_user_nickname} registrated successfully."
        log.log_info(msg_info)

        # VOICE RECOGNITION
        new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"
        new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
        os.mkdir(new_user_dir)
        manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)
        recordings_counter += 1

    frame_register_new_user.lower()
    frame_register_new_voiceprints.lift()
    clear_frames(registration_frames)

    if voiceprints_counter < const.NUMBER_OF_VOICEPRINTS:
        label_main_title = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                        text=Translations.get_translation('system_authentication'),
                                        font=("Roboto", 48, "bold"), justify=ctk.CENTER)
        label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

        label_second_phase = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                          text=Translations.get_translation('registration_second_phase'),
                                          font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
        label_second_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

        label_register_user = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                           text=Translations.get_translation(
                                               'register_come_closer_2') + "\n\n" + Translations.get_translation(
                                               'register_start_recording') + "\n\n" + Translations.get_translation(
                                               'recording_number') + str(voiceprints_counter + 1) + ".",
                                           font=("Roboto", 38), justify=ctk.LEFT)
        label_register_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

        button_back = ctk.CTkButton(master=frame_register_new_voiceprints, text=Translations.get_translation('back'),
                                    font=("Roboto", 38, "bold"),
                                    command=lambda: button_back_callback(frame_register_new_voiceprints,
                                                                         frame_authentication_success),
                                    width=275,
                                    height=70)
        button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

        button_registrate = ctk.CTkButton(master=frame_register_new_voiceprints,
                                          text=Translations.get_translation('registrate'),
                                          font=("Roboto", 38, "bold"),
                                          command=lambda: button_registrate_phase_2_callback(label_second_phase,
                                                                                             label_register_user,
                                                                                             button_back,
                                                                                             button_registrate),
                                          width=275,
                                          height=70)
        button_registrate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")
    else:
        voiceprints_counter = 0
        frame_registrate_new_unique_phrase_callback()


def button_registrate_phase_2_callback(label_second_phase, label_register_user, button_back, button_registrate):
    label_second_phase.destroy()
    label_register_user.configure(text=Translations.get_translation('recording'))
    button_back.destroy()
    button_registrate.destroy()
    window.update()

    global new_user_nickname, voiceprints_counter, recordings_counter
    voiceprints_counter += 1

    recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
    msg_info = f"Voiceprint recording no.{str(voiceprints_counter)} recorded successfully."
    log.log_info(msg_info)

    # VOICE RECOGNITION
    new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"
    new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
    manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)
    recordings_counter += 1

    label_register_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()

    time.sleep(1.5)
    window.update()

    msg_info = f"Voiceprint {voiceprints_counter} recorded successfully."
    log.log_info(msg_info)

    button_confirm_phase_1_callback()


# create REGISTER NEW UNIQUE PHRASE FRAME widgets
def frame_registrate_new_unique_phrase_callback():
    frame_register_new_voiceprints.lower()
    frame_registrate_new_unique_phrase.lift()
    clear_frames(registration_frames)

    label_main_title = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_third_phase = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                     text=Translations.get_translation('registration_third_phase'),
                                     font=("Roboto", 38, "bold"), text_color=("light green"), justify=ctk.CENTER)
    label_third_phase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_register_user = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                       text=Translations.get_translation(
                                           'register_come_closer_3') + "\n\n" + Translations.get_translation(
                                           'register_start_recording'),
                                       font=("Roboto", 38), justify=ctk.LEFT)
    label_register_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_registrate_new_unique_phrase, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_registrate_new_unique_phrase,
                                                                     frame_authentication_success),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_registrate = ctk.CTkButton(master=frame_registrate_new_unique_phrase,
                                      text=Translations.get_translation('registrate'),
                                      font=("Roboto", 38, "bold"),
                                      command=lambda: button_registrate_phase_3_callback(label_third_phase,
                                                                                         label_register_user,
                                                                                         button_back,
                                                                                         button_registrate),
                                      width=275,
                                      height=70)
    button_registrate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")


def button_registrate_phase_3_callback(label_third_phase, label_register_user, button_back, button_registrate):
    global new_user_unique_phrase

    label_third_phase.destroy()
    label_register_user.configure(text=Translations.get_translation('recording'))
    button_back.destroy()
    button_registrate.destroy()
    window.update()

    recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
    new_user_unique_phrase = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                           Translations.get_language().lower())
    new_user_unique_phrase = new_user_unique_phrase.lower()

    msg_info = f"Recognized new user unique phrase: {string_hasher.encode_string(new_user_unique_phrase)}"
    log.log_info(msg_info)

    label_register_user.configure(text=Translations.get_translation('recording_ended'))
    window.update()

    time.sleep(1.5)

    label_register_user.configure(text=Translations.get_translation('confirmation_phrase') + new_user_unique_phrase)

    button_repeat = ctk.CTkButton(master=frame_registrate_new_unique_phrase,
                                  text=Translations.get_translation('repeat'),
                                  font=("Roboto", 38, "bold"),
                                  command=button_repeat_phase_3_callback,
                                  width=275,
                                  height=70)
    button_repeat.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_confirm = ctk.CTkButton(master=frame_registrate_new_unique_phrase,
                                   text=Translations.get_translation('confirm'),
                                   font=("Roboto", 38, "bold"),
                                   command=lambda: button_confirm_phase_3_callback(label_register_user, button_repeat,
                                                                                   button_confirm),
                                   width=275,
                                   height=70)
    button_confirm.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    window.update()


def button_repeat_phase_3_callback():
    frame_registrate_new_unique_phrase_callback()


def button_confirm_phase_3_callback(label_register_user, button_repeat, button_confirm):
    global new_user_nickname, new_user_unique_phrase, users, recordings_counter
    msg_info = f"New unique phrase {string_hasher.encode_string(new_user_unique_phrase)} registrated successfully."
    log.log_info(msg_info)

    # VOICE RECOGNITION
    new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"
    new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
    manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)
    recordings_counter = 0

    label_register_user.destroy()
    button_repeat.destroy()
    button_confirm.destroy()

    label_registration_success = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                              text=Translations.get_translation('registration_success'),
                                              font=("Roboto", 38, "bold"), text_color=("light green"),
                                              justify=ctk.CENTER)
    label_registration_success.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")
    window.update()

    time.sleep(1.5)

    if json.add_user_to_json_file(users, new_user_nickname, string_hasher.encode_string(new_user_unique_phrase),
                                  const.USERS_FILENAME):
        output_dir = const.SPEAKER_VOICEPRINTS_DIR + new_user_nickname + "/"
        os.mkdir(output_dir)
        v_recognizer.create_voiceprints(classifier, new_user_dir, output_dir)
        msg_info = f"New user {new_user_nickname} registered successfully."
        log.log_info(msg_info)
        manager.remove_dir_with_files(new_user_dir)
        if os.path.isfile(const.RECORDED_AUDIO_FILENAME):
            os.remove(const.RECORDED_AUDIO_FILENAME)
    else:
        msg_warning = f"New user {new_user_nickname} couldn't be registered."
        log.log_warning(msg_warning)

    users = json.load_json_file(const.USERS_FILENAME)
    new_user_nickname = ""
    new_user_unique_phrase = ""

    frame_registrate_new_unique_phrase.lower()
    clear_frame(frame_registrate_new_unique_phrase)
    clear_global_variables()
    frame_intro.lift()

    window.update()


# create MANAGE USERS FRAME widgets
def button_manage_users_callback():
    clear_frame(frame_manage_users)
    frame_authentication_success.lower()
    frame_manage_users.lift()

    users_to_show = users.copy()
    del users_to_show[currently_logged_user]

    label_main_title = ctk.CTkLabel(master=frame_manage_users,
                                    text=Translations.get_translation('system_authentication'),
                                    font=("Roboto", 48, "bold"), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    combobox_users = ctk.CTkComboBox(master=frame_manage_users, values=list(users_to_show.keys()),
                                     font=("Roboto", 38, "bold"),
                                     dropdown_font=("Roboto", 38, "bold"), justify=ctk.CENTER, hover=True,
                                     command=combobox_users_callback)
    combobox_users.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_manage_users, text=Translations.get_translation('back'),
                                font=("Roboto", 38, "bold"),
                                command=lambda: button_back_callback(frame_manage_users,
                                                                     frame_authentication_success),
                                width=275,
                                height=70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_delete_user = ctk.CTkButton(master=frame_manage_users,
                                       text=Translations.get_translation('delete'),
                                       font=("Roboto", 38, "bold"),
                                       command=button_delete_user_callback,
                                       width=275,
                                       height=70)
    button_delete_user.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")


def combobox_users_callback(value):
    global user_to_delete
    user_to_delete = value


def button_delete_user_callback():
    global user_to_delete, users

    if user_to_delete in users.keys():
        if json.remove_user_from_json_file(users, user_to_delete, const.USERS_FILENAME):
            manager.remove_dir_with_files(const.SPEAKER_RECORDINGS_DIR + user_to_delete + "/")
            manager.remove_dir_with_files(const.SPEAKER_VOICEPRINTS_DIR + user_to_delete + "/")
            msg_info = f"User {user_to_delete} deleted successfully from the app database."
            log.log_info(msg_info)
        else:
            msg_warning = f"User {user_to_delete} not found in registered users."
            log.log_warning(msg_warning)

        users = json.load_json_file(const.USERS_FILENAME)
        user_to_delete = ""
        button_manage_users_callback()


authentication_frames = []
registration_frames = []

# create INTRO FRAME
frame_intro = create_frame()
frame_intro.lift()

# create ABOUT FRAME
frame_about = create_frame()
frame_about.lower()

# create OPEN DOOR FRAME
frame_open_door = create_frame()
frame_open_door.lower()

# create AUTHENTICATION PHASE 1 FRAME -> after click on SIGN IN button
frame_authentication_phase_1 = create_frame()
frame_authentication_phase_1.lower()
authentication_frames.append(frame_authentication_phase_1)

# create AUTHENTICATION PHASE 2 FRAME
frame_authentication_phase_2 = create_frame()
frame_authentication_phase_2.lower()
authentication_frames.append(frame_authentication_phase_2)

# create AUTHENTICATION PHASE 3 FRAME
frame_authentication_phase_3 = create_frame()
frame_authentication_phase_3.lower()
authentication_frames.append(frame_authentication_phase_3)

# create AUTHENTICATION SUCCESS FRAME
frame_authentication_success = create_frame()
frame_authentication_success.lower()

# create AUTHENTICATION UNSUCCESS FRAME
frame_authentication_unsuccess = create_frame()
frame_authentication_unsuccess.lower()
authentication_frames.append(frame_authentication_unsuccess)

# create REGISTRATION FRAME
frame_registraction = create_frame()
frame_registraction.lower()
authentication_frames.append(frame_registraction)

# create REGISTER NEW USER FRAME
frame_register_new_user = create_frame()
frame_register_new_user.lower()
registration_frames.append(frame_register_new_user)

# create REGISTER NEW VOICEPRINTS FRAME
frame_register_new_voiceprints = create_frame()
frame_register_new_voiceprints.lower()
registration_frames.append(frame_register_new_voiceprints)

# create REGISTER NEW UNIQUE PHRASE FRAME
frame_registrate_new_unique_phrase = create_frame()
frame_registrate_new_unique_phrase.lower()
registration_frames.append(frame_registrate_new_unique_phrase)

# create MANAGE USERS FRAME
frame_manage_users = create_frame()
frame_manage_users.lower()

# create NOT INTERNET CONNECTION FRAME
frame_not_internet_connection = create_frame()
frame_not_internet_connection.lower()

# create INTRO FRAME widgets
label_main_title = ctk.CTkLabel(master=frame_intro, text=Translations.get_translation('system_authentication'),
                                font=("Roboto", 48, "bold"), justify=ctk.CENTER)
label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

button_open_door = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('open_door'),
                                 font=("Roboto", 48, "bold"), command=button_open_door_callback)
button_open_door.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

button_about_project = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('about_project'),
                                     font=("Roboto", 38, "bold"), command=button_about_project_callback, width=150,
                                     height=50)
button_about_project.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

button_exit = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('exit'), font=("Roboto", 38, "bold"),
                            command=button_exit_callback, width=150, height=50)
button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

segmented_button_language = ctk.CTkSegmentedButton(master=frame_intro, values=["SK", "EN"], font=("Roboto", 38, "bold"),
                                                   command=segmented_button_language_callback, width=150, height=50)
segmented_button_language.grid(row=6, column=7, pady=10, padx=10, sticky="nsew")

is_internet_connection = conn.check_internet_connection()
users = json.load_json_file(const.USERS_FILENAME)
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                            savedir=r"pretrained_models/spkrec-ecapa-voxceleb",
                                            run_opts={"device": "cpu"})


def disable_minimize(event):
    window.overrideredirect(True)


window.bind("<Map>", disable_minimize)

window.mainloop()
