import os
import time
import customtkinter as ctk
import tkinter as tk
import RPi.GPIO as GPIO

from speechbrain.inference import EncoderClassifier
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
from database import db_operations as db

user_to_delete = ""
currently_logged_user = ""
new_user_nickname = ""
new_user_unique_phrase = ""

remaining_attempts = 3
voiceprints_counter = 0
recordings_counter = 0
registration_with_internet = True
is_admin_logged = False
partial_authentication = 0.0

relayPin = const.RELAY_PIN
buzzerPin = const.BUZZER_PIN
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relayPin, GPIO.OUT)
GPIO.setup(buzzerPin, GPIO.OUT)

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

font_roboto = const.FONT_ROBOTO
font_bold = const.FONT_BOLD
font_48 = const.FONT_48
font_42 = const.FONT_42
font_38 = const.FONT_38
font_36 = const.FONT_36
font_32 = const.FONT_32
width_275 = const.WIDTH_275
width_150 = const.WIDTH_150
height_100 = const.HEIGHT_100
height_70 = const.HEIGHT_70
height_60 = const.HEIGHT_60
height_50 = const.HEIGHT_50

if width == 1280 and height == 720:
    font_48 = round(font_48 / 1.5)
    font_42 = round(font_42 / 1.5)
    font_38 = round(font_38 / 1.5)
    font_36 = round(font_36 / 1.5)
    font_32 = round(font_32 / 1.5)
    width_275 = round(width_275 / 1.5)
    width_150 = round(width_150 / 1.5)
    height_100 = round(height_100 / 1.5)
    height_70 = round(height_70 / 1.5)
    height_60 = round(height_60 / 1.5)
    height_50 = round(height_50 / 1.5)


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
    global user_to_delete, currently_logged_user, new_user_nickname, new_user_unique_phrase, remaining_attempts, voiceprints_counter, recordings_counter, registration_with_internet, is_admin_logged
    user_to_delete = ""
    currently_logged_user = ""
    new_user_nickname = ""
    new_user_unique_phrase = ""
    remaining_attempts = 3
    voiceprints_counter = 0
    recordings_counter = 0
    registration_with_internet = True
    is_admin_logged = False


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
    global is_admin_logged
    is_admin_logged = False

    frame_intro.lower()
    frame_open_door.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_open_door, text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('exit'),
                                font=(font_roboto, font_38, font_bold),
                                command=button_exit_callback, width=width_150, height=height_50)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_open_door, frame_intro), width=width_150,
                                height=height_50)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_sign_in = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_in'),
                                   font=(font_roboto, font_48, font_bold), command=button_sign_in_callback)
    button_sign_in.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_sign_up = ctk.CTkButton(master=frame_open_door, text=Translations.get_translation('sign_up'),
                                   font=(font_roboto, font_48, font_bold), command=button_sign_up_callback)
    button_sign_up.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")


# create ABOUT FRAME widgets
def button_about_project_callback():
    global is_admin_logged
    is_admin_logged = False

    frame_intro.lower()
    frame_about.lift()

    label_main_title = ctk.CTkLabel(master=frame_about, text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_about, text=Translations.get_translation('exit'),
                                font=(font_roboto, font_38, font_bold),
                                command=button_exit_callback, width=width_150, height=height_100)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_about, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_about, frame_intro), width=width_150,
                                height=height_100)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    label_thesis = ctk.CTkLabel(master=frame_about, text=Translations.get_translation('thesis'),
                                font=(font_roboto, font_42, font_bold), justify=ctk.CENTER)
    label_thesis.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    label_about_project = ctk.CTkLabel(master=frame_about,
                                       text=Translations.get_translation('topic') + "\n" + Translations.get_translation(
                                           'student') + "\n" + Translations.get_translation(
                                           'mentor') + "\n" + Translations.get_translation('year'),
                                       font=(font_roboto, font_32), justify=ctk.LEFT)
    label_about_project.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_school = ctk.CTkLabel(master=frame_about, text=(
            Translations.get_translation('university') + "\n\n" + Translations.get_translation(
        'faculty') + "\n\n" + Translations.get_translation('department')), font=(font_roboto, font_32),
                                justify=ctk.CENTER)
    label_school.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")

    entry_password = ctk.CTkEntry(master=frame_about, font=(font_roboto, font_38, font_bold), placeholder_text="",
                                  show="*",
                                  justify=ctk.CENTER, width=width_150, height=height_100)
    entry_password.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_password = ctk.CTkButton(master=frame_about, text=Translations.get_translation('confirm'),
                                    font=(font_roboto, font_38, font_bold),
                                    command=lambda: button_password_callback(entry_password.get(), "authentication"),
                                    width=width_150,
                                    height=height_100)
    button_password.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_exit_callback():
    window.destroy()


def segmented_button_language_callback(value):
    change_language(value)


def button_admin_callback():
    frame_intro.lower()
    frame_admin.lift()

    label_main_title = ctk.CTkLabel(master=frame_admin, text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_admin, text=Translations.get_translation('exit'),
                                font=(font_roboto, font_38, font_bold),
                                command=button_exit_callback, width=width_150, height=height_60)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_admin, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_admin, frame_intro), width=width_150,
                                height=height_60)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    label_admin_info = ctk.CTkLabel(master=frame_admin,
                                    text=Translations.get_translation('admin_interface'),
                                    font=(font_roboto, font_36), justify=ctk.LEFT)
    label_admin_info.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    entry_password = ctk.CTkEntry(master=frame_admin, font=(font_roboto, font_38, font_bold), placeholder_text="",
                                  show="*",
                                  justify=ctk.CENTER, width=width_150, height=height_60)
    entry_password.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_password = ctk.CTkButton(master=frame_admin, text=Translations.get_translation('confirm'),
                                    font=(font_roboto, font_38, font_bold),
                                    command=lambda: button_password_callback(entry_password.get(), "admin"),
                                    width=width_150,
                                    height=height_60)
    button_password.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_back_callback(frame_to_hide, frame_to_show):
    global voiceprints_counter
    voiceprints_counter = 0
    clear_frame(frame_to_hide)
    frame_to_hide.lower()
    frame_to_show.lift()
    window.update()


def button_password_callback(value, phase):
    global is_admin_logged

    correct_password = False

    if phase == "authentication":
        correct_password = string_hasher.check_string(value, credentials.authentication_password,
                                                      credentials.authentication_salt)

    if phase == "admin":
        correct_password = string_hasher.check_string(value, credentials.admin_password, credentials.admin_salt)

    if correct_password:
        if phase == "authentication":
            is_admin_logged = False
            if conn.check_internet_connection():
                frame_about.lower()
            else:
                frame_not_internet_connection.lower()

            button_open_door_callback()
            frame_open_door.lower()
            frame_authentication_phase_3_callback()

        if phase == "admin":
            is_admin_logged = True
            frame_admin.lower()
            frame_authentication_success_callback()

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
                                        font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
        label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

        label_first_phase = ctk.CTkLabel(master=frame_authentication_phase_1,
                                         text=Translations.get_translation('first_phase'),
                                         font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                         justify=ctk.CENTER)
        label_first_phase.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

        progress_bar_authentication = ctk.CTkProgressBar(master=frame_authentication_phase_1)
        progress_bar_authentication.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")
        progress_bar_authentication.set(1 / 3)

        label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_1,
                                               text=Translations.get_translation(
                                                   'come_closer_1') + "\n\n" + Translations.get_translation(
                                                   'start_recording'),
                                               font=(font_roboto, font_38), justify=ctk.LEFT)
        label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

        button_back = ctk.CTkButton(master=frame_authentication_phase_1, text=Translations.get_translation('back'),
                                    font=(font_roboto, font_38, font_bold),
                                    command=lambda: button_back_callback(frame_authentication_phase_1, frame_open_door),
                                    width=width_275,
                                    height=height_70)
        button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

        button_authenticate = ctk.CTkButton(master=frame_authentication_phase_1,
                                            text=Translations.get_translation('authenticate'),
                                            font=(font_roboto, font_38, font_bold),
                                            command=lambda: button_authenticate_phase_1_callback(label_first_phase,
                                                                                                 label_authenticate_user,
                                                                                                 button_back,
                                                                                                 button_authenticate,
                                                                                                 progress_bar_authentication),
                                            width=width_275,
                                            height=height_70)
        button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

        window.update()
    else:
        frame_not_internet_connection_callback()


def frame_not_internet_connection_callback():
    frame_not_internet_connection.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_not_internet_connection,
                                    text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_not_connection = ctk.CTkLabel(master=frame_not_internet_connection,
                                        text=Translations.get_translation('internet'),
                                        font=(font_roboto, font_38, font_bold), text_color="red", justify=ctk.CENTER)
    label_not_connection.grid(row=3, column=4, sticky="nsew")

    label_limited_mode = ctk.CTkLabel(master=frame_not_internet_connection,
                                      text=Translations.get_translation(
                                          'limited_mode') + "\n\n" + Translations.get_translation(
                                          'password_to_continue'),
                                      font=(font_roboto, font_38), justify=ctk.LEFT)
    label_limited_mode.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_exit = ctk.CTkButton(master=frame_not_internet_connection, text=Translations.get_translation('exit'),
                                font=(font_roboto, font_38, font_bold),
                                command=button_exit_callback, width=width_150, height=height_60)
    button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_not_internet_connection, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_not_internet_connection, frame_open_door),
                                width=width_150, height=height_60)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    entry_password = ctk.CTkEntry(master=frame_not_internet_connection, font=(font_roboto, font_38, font_bold),
                                  placeholder_text="", show="*",
                                  justify=ctk.CENTER, width=width_150, height=height_60)
    entry_password.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_password = ctk.CTkButton(master=frame_not_internet_connection, text=Translations.get_translation('confirm'),
                                    font=(font_roboto, font_38, font_bold),
                                    command=lambda: button_password_callback(entry_password.get(), "authentication"),
                                    width=width_150,
                                    height=height_60)
    button_password.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")


def button_authenticate_phase_1_callback(label_first_phase, label_authenticate_user, button_back, button_authenticate,
                                         progress_bar_authentication):
    global currently_logged_user, partial_authentication

    label_first_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()
    progress_bar_authentication.destroy()

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
        label_authenticate_user.configure(text=Translations.get_translation('recording'),
                                          font=(font_roboto, font_38, font_bold), justify=ctk.CENTER)
        label_short_info = ctk.CTkLabel(master=frame_authentication_phase_1,
                                        text=Translations.get_translation(
                                            'short_info_1'),
                                        font=(font_roboto, font_38, font_bold), corner_radius=20, fg_color="#696969",
                                        justify=ctk.CENTER)
        label_short_info.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")
        window.update()

        # SPEECH RECOGNITION
        recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
        speaker_nickname = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                         Translations.get_language().lower())
        speaker_nickname = speaker_nickname.lower()
        speaker_exists = s_recognizer.verify_speaker_nickname(users.keys(), speaker_nickname)

        msg_info = f"Recognized speaker nickname: {speaker_nickname}"
        log.log_info(msg_info)

        label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
        window.update()

        time.sleep(1.5)

        if speaker_exists:
            currently_logged_user = speaker_nickname.lower()

            if s_recognizer.user_registered_with_internet(users, currently_logged_user):
                speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + speaker_nickname + "/"
                # login_success = v_recognizer.verify_speaker(classifier, speaker_dir, const.RECORDED_AUDIO_FILENAME)
                login_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                           const.RECORDED_AUDIO_FILENAME,
                                                                           auth_weight=10)
                partial_authentication = partial_authentication + score
            else:
                login_success = speaker_exists

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
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_sign_in_success = ctk.CTkLabel(master=frame_authentication_phase_2,
                                         text=Translations.get_translation('sign_in_success'),
                                         font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                         justify=ctk.CENTER)
    label_sign_in_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    time.sleep(1.5)

    label_sign_in_success.destroy()

    label_second_phase = ctk.CTkLabel(master=frame_authentication_phase_2,
                                      text=Translations.get_translation('second_phase'),
                                      font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                      justify=ctk.CENTER)
    label_second_phase.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    progress_bar_authentication = ctk.CTkProgressBar(master=frame_authentication_phase_2)
    progress_bar_authentication.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")
    progress_bar_authentication.set(2 / 3)

    label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_2,
                                           text=Translations.get_translation(
                                               'come_closer_2') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=(font_roboto, font_38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_authentication_phase_2, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_authentication_phase_2, frame_open_door),
                                width=width_275,
                                height=height_70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_authentication_phase_2,
                                        text=Translations.get_translation('authenticate'),
                                        font=(font_roboto, font_38, font_bold),
                                        command=lambda: button_authenticate_phase_2_callback(label_second_phase,
                                                                                             label_authenticate_user,
                                                                                             button_back,
                                                                                             button_authenticate,
                                                                                             progress_bar_authentication),
                                        width=width_275,
                                        height=height_70)
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    window.update()


def button_authenticate_phase_2_callback(label_second_phase, label_authenticate_user, button_back, button_authenticate,
                                         progress_bar_authentication):
    global partial_authentication
    label_second_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()
    progress_bar_authentication.destroy()

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
                                         font=(font_roboto, font_48, font_bold), text_color=("light green"),
                                         justify=ctk.CENTER)
        label_random_word.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

        label_authenticate_user.configure(text=Translations.get_translation('recording'),
                                          font=(font_roboto, font_38, font_bold), justify=ctk.CENTER)
        label_short_info = ctk.CTkLabel(master=frame_authentication_phase_2,
                                        text=Translations.get_translation(
                                            'short_info_2'),
                                        font=(font_roboto, font_38, font_bold), corner_radius=20, fg_color="#696969",
                                        justify=ctk.CENTER)
        label_short_info.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")
        window.update()

        # SPEECH RECOGNITION
        recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
        spoken_verification_word = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                                 Translations.get_language().lower())
        spoken_verification_word_matches = s_recognizer.verify_verification_word(spoken_verification_word, random_word)

        msg_info = f"Recognized verification word: {spoken_verification_word}"
        log.log_info(msg_info)

        label_authenticate_user.configure(text=Translations.get_translation('recording_ended'))
        label_random_word.destroy()
        window.update()

        time.sleep(1.5)

        if spoken_verification_word_matches:
            speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + currently_logged_user + "/"
            # verification_success = v_recognizer.verify_speaker(classifier, speaker_dir, const.RECORDED_AUDIO_FILENAME)
            verification_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                              const.RECORDED_AUDIO_FILENAME,
                                                                              auth_weight=20)
            partial_authentication = partial_authentication + score

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
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_verification_success = ctk.CTkLabel(master=frame_authentication_phase_3,
                                              text=Translations.get_translation('verification_success'),
                                              font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                              justify=ctk.CENTER)
    label_verification_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    time.sleep(1.5)

    label_verification_success.destroy()

    label_third_phase = ctk.CTkLabel(master=frame_authentication_phase_3,
                                     text=Translations.get_translation('third_phase'),
                                     font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                     justify=ctk.CENTER)
    label_third_phase.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    progress_bar_authentication = ctk.CTkProgressBar(master=frame_authentication_phase_3)
    progress_bar_authentication.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")
    progress_bar_authentication.set(3 / 3)

    label_authenticate_user = ctk.CTkLabel(master=frame_authentication_phase_3,
                                           text=Translations.get_translation(
                                               'come_closer_3') + "\n\n" + Translations.get_translation(
                                               'start_recording'),
                                           font=(font_roboto, font_38), justify=ctk.LEFT)
    label_authenticate_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_authentication_phase_3, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_authentication_phase_3, frame_open_door),
                                width=width_275,
                                height=height_70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_authenticate = ctk.CTkButton(master=frame_authentication_phase_3,
                                        text=Translations.get_translation('authenticate'),
                                        font=(font_roboto, font_38, font_bold),
                                        command=lambda: button_authenticate_phase_3_callback(label_third_phase,
                                                                                             label_authenticate_user,
                                                                                             button_back,
                                                                                             button_authenticate,
                                                                                             progress_bar_authentication),
                                        width=width_275,
                                        height=height_70)
    button_authenticate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

    window.update()


def button_authenticate_phase_3_callback(label_third_phase, label_authenticate_user, button_back, button_authenticate,
                                         progress_bar_authentication):
    global currently_logged_user, partial_authentication
    skipped_phases = False

    label_third_phase.destroy()
    button_back.destroy()
    button_authenticate.destroy()
    progress_bar_authentication.destroy()

    label_authenticate_user.configure(text=Translations.get_translation('recording'),
                                      font=(font_roboto, font_38, font_bold), justify=ctk.CENTER)
    label_short_info = ctk.CTkLabel(master=frame_authentication_phase_3,
                                    text=Translations.get_translation(
                                        'short_info_3'),
                                    font=(font_roboto, font_38, font_bold), corner_radius=20, fg_color="#696969",
                                    justify=ctk.CENTER)
    label_short_info.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")
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
            skipped_phases = True

            if unique_phrase != "":
                if not s_recognizer.verify_unique_phrase(users, currently_logged_user, unique_phrase):
                    currently_logged_user = ""

        if currently_logged_user != "":
            speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + currently_logged_user + "/"
            # authentication_success = v_recognizer.verify_speaker(classifier, speaker_dir,
            #                                                     const.RECORDED_AUDIO_FILENAME)

            if not skipped_phases:
                authentication_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                                    const.RECORDED_AUDIO_FILENAME,
                                                                                    auth_weight=70)
            else:
                authentication_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                                    const.RECORDED_AUDIO_FILENAME)

            partial_authentication = partial_authentication + score

            msg_success = f"Final result of partial authentication is {partial_authentication} %."
            log.log_info(msg_success)

            if authentication_success:
                msg_success = f"Authentication with unique phrase was successful. User {currently_logged_user} opened the door."
                log.log_info(msg_success)

                if partial_authentication >= const.PARTIAL_AUTHORIZATION_THRESHOLD:
                    if os.path.isfile(const.RECORDED_AUDIO_FILENAME):
                        os.remove(const.RECORDED_AUDIO_FILENAME)
                    frame_authentication_success_callback()
                else:
                    msg_warning = f"Final result of partial authentication is under the threshold."
                    log.log_warning(msg_warning)
                    partial_authentication = partial_authentication - score
                    frame_authentication_unsuccess_callback(3)
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
    global remaining_attempts, is_internet_connection, currently_logged_user, is_admin_logged
    remaining_attempts = 3

    is_internet_connection = conn.check_internet_connection()

    clear_frame(frame_authentication_success)
    frame_authentication_phase_3.lower()
    frame_authentication_success.lift()

    label_main_title = ctk.CTkLabel(master=frame_authentication_success,
                                    text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_authentication_success = ctk.CTkLabel(master=frame_authentication_success,
                                                text=Translations.get_translation('authentication_success'),
                                                font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                                justify=ctk.CENTER)
    label_authentication_success.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    GPIO.output(relayPin, True)
    GPIO.output(buzzerPin, GPIO.HIGH)

    time.sleep(5)

    GPIO.output(relayPin, False)
    GPIO.output(buzzerPin, GPIO.LOW)

    label_authentication_success.destroy()

    if is_admin_logged:
        currently_logged_user = "admin"

    label_logged_user = ctk.CTkLabel(master=frame_authentication_success,
                                     text=Translations.get_translation('logged_user') + currently_logged_user,
                                     font=(font_roboto, font_38, font_bold), text_color="light green",
                                     justify=ctk.CENTER)
    label_logged_user.grid(row=2, column=4, sticky="nsew")

    button_end_interaction = ctk.CTkButton(master=frame_authentication_success,
                                           text=Translations.get_translation('end_interaction'),
                                           font=(font_roboto, font_48, font_bold),
                                           command=button_end_interaction_callback)
    button_end_interaction.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_register_user = ctk.CTkButton(master=frame_authentication_success,
                                         text=Translations.get_translation('register_user'),
                                         font=(font_roboto, font_48, font_bold), command=button_register_user_callback)
    button_register_user.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")

    button_manage_users = ctk.CTkButton(master=frame_authentication_success,
                                        text=Translations.get_translation('manage_users'),
                                        font=(font_roboto, font_48, font_bold), command=button_manage_users_callback)

    if const.IS_ADMIN and is_internet_connection:
        button_manage_users.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")
    else:
        button_manage_users.destroy()


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
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_authentication_unsuccess = ctk.CTkLabel(master=frame_authentication_unsuccess,
                                                  text=Translations.get_translation('authentication_unsuccess'),
                                                  font=(font_roboto, font_38, font_bold), text_color=("red"),
                                                  justify=ctk.CENTER)
    label_authentication_unsuccess.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_authentication_unsuccess_info = ctk.CTkLabel(master=frame_authentication_unsuccess,
                                                       text=Translations.get_translation(
                                                           'authentication_unsuccess_info') + "\n\n" + Translations.get_translation(
                                                           'remaining_attempts') + str(
                                                           remaining_attempts) + "\n\n" + Translations.get_translation(
                                                           'start_authentication_again'),
                                                       font=(font_roboto, font_38), justify=ctk.LEFT)
    label_authentication_unsuccess_info.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_authenticate_again = ctk.CTkButton(master=frame_authentication_unsuccess,
                                              text=Translations.get_translation('authenticate_again'),
                                              font=(font_roboto, font_48, font_bold),
                                              command=lambda: button_authenticate_again_callback(phase),
                                              width=width_150,
                                              height=height_100)
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
    frame_registration.lift()
    clear_frames(authentication_frames)

    label_main_title = ctk.CTkLabel(master=frame_registration,
                                    text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_registration = ctk.CTkLabel(master=frame_registration,
                                      text=Translations.get_translation(
                                          'registration_info') + "\n\n" + Translations.get_translation(
                                          'continue_to_sign_in'),
                                      font=(font_roboto, font_38), justify=ctk.LEFT)
    label_registration.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    button_sign_in_again = ctk.CTkButton(master=frame_registration, text=Translations.get_translation('sign_in'),
                                         font=(font_roboto, font_48, font_bold), command=button_sign_in_callback)
    button_sign_in_again.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")


# create REGISTER NEW USER FRAME widgets
def button_register_user_callback():
    frame_authentication_success.lower()
    frame_register_new_user.lift()
    clear_frames(registration_frames)

    label_main_title = ctk.CTkLabel(master=frame_register_new_user,
                                    text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_first_phase = ctk.CTkLabel(master=frame_register_new_user,
                                     text=Translations.get_translation('registration_first_phase'),
                                     font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                     justify=ctk.CENTER)
    label_first_phase.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    progress_bar_authentication = ctk.CTkProgressBar(master=frame_register_new_user)
    progress_bar_authentication.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")
    progress_bar_authentication.set(1 / (2 + const.NUMBER_OF_VOICEPRINTS))

    label_register_user = ctk.CTkLabel(master=frame_register_new_user,
                                       text=Translations.get_translation(
                                           'register_come_closer_1') + "\n\n" + Translations.get_translation(
                                           'register_start_recording'),
                                       font=(font_roboto, font_38), justify=ctk.LEFT)
    label_register_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_register_new_user, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_register_new_user,
                                                                     frame_authentication_success),
                                width=width_275,
                                height=height_70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_registrate = ctk.CTkButton(master=frame_register_new_user,
                                      text=Translations.get_translation('registrate'),
                                      font=(font_roboto, font_38, font_bold),
                                      command=lambda: button_registrate_phase_1_callback(label_first_phase,
                                                                                         label_register_user,
                                                                                         button_back,
                                                                                         button_registrate,
                                                                                         progress_bar_authentication),
                                      width=width_275,
                                      height=height_70)
    button_registrate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")


def button_registrate_phase_1_callback(label_first_phase, label_register_user, button_back, button_registrate,
                                       progress_bar_authentication):
    global new_user_nickname, is_internet_connection, voiceprints_phrases, registration_with_internet

    voiceprints_phrases = list(const.VOICEPRINT_PHRASES[Translations.get_language()])
    is_internet_connection = conn.check_internet_connection()
    registration_with_internet = is_internet_connection

    if is_internet_connection:
        label_first_phase.destroy()
        button_back.destroy()
        button_registrate.destroy()
        progress_bar_authentication.destroy()

        label_register_user.configure(text=Translations.get_translation('recording'),
                                      font=(font_roboto, font_38, font_bold), justify=ctk.CENTER)
        label_short_info = ctk.CTkLabel(master=frame_register_new_user,
                                        text=Translations.get_translation(
                                            'short_info_1'),
                                        font=(font_roboto, font_38, font_bold), corner_radius=20, fg_color="#696969",
                                        justify=ctk.CENTER)
        label_short_info.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")
        window.update()

        # SPEECH recognition
        recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
        new_user_nickname = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                          Translations.get_language().lower())
        new_user_nickname = new_user_nickname.lower()

        msg_info = f"Recognized new user nickname: {new_user_nickname}"
        log.log_info(msg_info)

        label_register_user.configure(text=Translations.get_translation('recording_ended'))
        label_short_info.destroy()
        window.update()

        time.sleep(1.5)

        label_register_user.configure(text=Translations.get_translation('confirmation_nickname') + new_user_nickname)

        button_repeat = ctk.CTkButton(master=frame_register_new_user, text=Translations.get_translation('repeat'),
                                      font=(font_roboto, font_38, font_bold),
                                      command=button_repeat_phase_1_callback,
                                      width=width_275,
                                      height=height_70)
        button_repeat.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

        button_confirm = ctk.CTkButton(master=frame_register_new_user,
                                       text=Translations.get_translation('confirm'),
                                       font=(font_roboto, font_38, font_bold),
                                       command=button_confirm_phase_1_callback,
                                       width=width_275,
                                       height=height_70, state="normal")
        button_confirm.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

        if new_user_nickname in users:
            button_confirm.configure(state="disabled")
            label_register_user.configure(
                text=Translations.get_translation(
                    'nickname_exists_1') + new_user_nickname + Translations.get_translation(
                    'nickname_exists_2') + "\n\n" + Translations.get_translation('nickname_exists_3'),
                font=(font_roboto, font_38, font_bold), text_color="red")

        window.update()
    else:
        frame_register_not_internet_callback("nickname", None, None, None)


def frame_register_not_internet_callback(phase, label_register_user, button_repeat, button_confirm):
    frame_register_not_internet.lift()

    label_main_title = ctk.CTkLabel(master=frame_register_not_internet,
                                    text=Translations.get_translation('system_authentication'),
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_not_connection = ctk.CTkLabel(master=frame_register_not_internet,
                                        text=Translations.get_translation('internet'),
                                        font=(font_roboto, font_38, font_bold), text_color="red", justify=ctk.CENTER)
    label_not_connection.grid(row=3, column=4, sticky="nsew")

    label_register_user = ctk.CTkLabel(master=frame_register_not_internet,
                                       text=Translations.get_translation(
                                           'nickname_exists_1') + new_user_nickname + Translations.get_translation(
                                           'nickname_exists_2') + "\n\n" + Translations.get_translation(
                                           'nickname_exists_3'),
                                       font=(font_roboto, font_32, font_bold), text_color="red", justify=ctk.LEFT)

    entry_register = ctk.CTkEntry(master=frame_register_not_internet, font=(font_roboto, font_38, font_bold),
                                  placeholder_text="",
                                  justify=ctk.CENTER, width=width_150, height=height_60)
    entry_register.grid(row=6, column=4, pady=10, padx=10, sticky="nsew")

    button_confirm = ctk.CTkButton(master=frame_register_not_internet,
                                   text=Translations.get_translation('confirm'),
                                   font=(font_roboto, font_38, font_bold),
                                   command=lambda: button_confirm_register_callback(entry_register.get(), phase,
                                                                                    label_register_user, button_repeat,
                                                                                    button_confirm), width=width_150,
                                   height=height_60)
    button_confirm.grid(row=7, column=4, pady=10, padx=10, sticky="nsew")

    if phase == "nickname":
        label_limited_mode = ctk.CTkLabel(master=frame_register_not_internet,
                                          text=Translations.get_translation(
                                              'limited_mode') + "\n\n" + Translations.get_translation(
                                              'nickname_to_continue'),
                                          font=(font_roboto, font_38), justify=ctk.LEFT)
        label_limited_mode.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

        if new_user_nickname in users:
            label_register_user.grid(row=5, column=4, pady=10, padx=10, sticky="nsew")
        else:
            label_register_user.destroy()

    elif phase == "unique_phrase":
        label_limited_mode = ctk.CTkLabel(master=frame_register_not_internet,
                                          text=Translations.get_translation(
                                              'limited_mode') + "\n\n" + Translations.get_translation(
                                              'phrase_to_continue'),
                                          font=(font_roboto, font_38), justify=ctk.LEFT)
        label_limited_mode.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")


def button_confirm_register_callback(value, phase, label_register_user, button_repeat, button_confirm):
    global new_user_nickname, new_user_unique_phrase

    if phase == "nickname":
        new_user_nickname = value.lower()
        if new_user_nickname in users:
            frame_register_not_internet_callback(phase, label_register_user, button_repeat, button_confirm)
        else:
            button_confirm_phase_1_callback()
    elif phase == "unique_phrase":
        new_user_unique_phrase = value.lower()
        button_confirm_phase_3_callback(label_register_user, button_repeat, button_confirm)


def button_repeat_phase_1_callback():
    button_register_user_callback()


# create REGISTER NEW VOICEPRINTS FRAME widgets
def button_confirm_phase_1_callback():
    global new_user_nickname, voiceprints_counter, recordings_counter

    number_of_voiceprints = const.NUMBER_OF_VOICEPRINTS

    if not is_internet_connection:
        number_of_voiceprints = number_of_voiceprints + 2

    if voiceprints_counter == 0:
        msg_info = f"New user nickname {new_user_nickname} registrated successfully."
        log.log_info(msg_info)

        # VOICE RECOGNITION
        if not os.path.isdir(const.SPEAKER_RECORDINGS_DIR):
            os.mkdir(const.SPEAKER_RECORDINGS_DIR)

        new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"

        if not os.path.isdir(new_user_dir):
            os.mkdir(new_user_dir)

        if is_internet_connection:
            new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
            manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)
            recordings_counter += 1

    frame_register_new_user.lower()
    frame_register_not_internet.lower()
    frame_register_new_voiceprints.lift()
    clear_frames(registration_frames)

    if voiceprints_counter < number_of_voiceprints:
        label_main_title = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                        text=Translations.get_translation('system_authentication'),
                                        font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
        label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

        label_second_phase = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                          text=Translations.get_translation('registration_second_phase'),
                                          font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                          justify=ctk.CENTER)
        label_second_phase.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

        progress_bar_authentication = ctk.CTkProgressBar(master=frame_register_new_voiceprints)
        progress_bar_authentication.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")
        progress_bar_authentication.set((recordings_counter + 1) / (2 + number_of_voiceprints))

        label_register_user = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                           text=Translations.get_translation(
                                               'register_come_closer_2') + "\n\n" + Translations.get_translation(
                                               'register_start_recording') + "\n\n" + Translations.get_translation(
                                               'recording_number') + str(voiceprints_counter + 1) + ".",
                                           font=(font_roboto, font_38), justify=ctk.LEFT)
        label_register_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

        button_back = ctk.CTkButton(master=frame_register_new_voiceprints, text=Translations.get_translation('back'),
                                    font=(font_roboto, font_38, font_bold),
                                    command=lambda: button_back_callback(frame_register_new_voiceprints,
                                                                         frame_authentication_success),
                                    width=width_275,
                                    height=height_70)
        button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

        button_registrate = ctk.CTkButton(master=frame_register_new_voiceprints,
                                          text=Translations.get_translation('registrate'),
                                          font=(font_roboto, font_38, font_bold),
                                          command=lambda: button_registrate_phase_2_callback(label_second_phase,
                                                                                             label_register_user,
                                                                                             button_back,
                                                                                             button_registrate,
                                                                                             progress_bar_authentication),
                                          width=width_275,
                                          height=height_70)
        button_registrate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")
    else:
        voiceprints_counter = 0
        frame_registrate_new_unique_phrase_callback()


def button_registrate_phase_2_callback(label_second_phase, label_register_user, button_back, button_registrate,
                                       progress_bar_authentication):
    global new_user_nickname, voiceprints_counter, recordings_counter, voiceprints_phrases

    random_phrase = s_recognizer.generate_random_word(voiceprints_phrases)
    voiceprints_phrases.remove(random_phrase)

    label_random_phrase = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                       text=random_phrase,
                                       font=(font_roboto, font_36, font_bold), text_color=("light green"),
                                       justify=ctk.CENTER)
    label_random_phrase.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_second_phase.destroy()
    button_back.destroy()
    button_registrate.destroy()
    progress_bar_authentication.destroy()

    label_register_user.configure(text=Translations.get_translation('recording'),
                                  font=(font_roboto, font_38, font_bold), justify=ctk.CENTER)
    label_short_info = ctk.CTkLabel(master=frame_register_new_voiceprints,
                                    text=Translations.get_translation(
                                        'short_info_2'),
                                    font=(font_roboto, font_38, font_bold), corner_radius=20, fg_color="#696969",
                                    justify=ctk.CENTER)
    label_short_info.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")
    window.update()

    voiceprints_counter += 1

    recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME, 6)
    msg_info = f"Voiceprint recording no.{str(voiceprints_counter)} recorded successfully."
    log.log_info(msg_info)

    # VOICE RECOGNITION
    new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"
    new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
    manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)
    recordings_counter += 1

    label_register_user.configure(text=Translations.get_translation('recording_ended'))
    label_random_phrase.destroy()
    label_short_info.destroy()
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
                                    font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
    label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

    label_third_phase = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                     text=Translations.get_translation('registration_third_phase'),
                                     font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                     justify=ctk.CENTER)
    label_third_phase.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")

    progress_bar_authentication = ctk.CTkProgressBar(master=frame_registrate_new_unique_phrase)
    progress_bar_authentication.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")
    progress_bar_authentication.set(1)

    label_register_user = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                       text=Translations.get_translation(
                                           'register_come_closer_3') + "\n\n" + Translations.get_translation(
                                           'register_start_recording'),
                                       font=(font_roboto, font_38), justify=ctk.LEFT)
    label_register_user.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    button_back = ctk.CTkButton(master=frame_registrate_new_unique_phrase, text=Translations.get_translation('back'),
                                font=(font_roboto, font_38, font_bold),
                                command=lambda: button_back_callback(frame_registrate_new_unique_phrase,
                                                                     frame_authentication_success),
                                width=width_275,
                                height=height_70)
    button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

    button_registrate = ctk.CTkButton(master=frame_registrate_new_unique_phrase,
                                      text=Translations.get_translation('registrate'),
                                      font=(font_roboto, font_38, font_bold),
                                      command=lambda: button_registrate_phase_3_callback(label_third_phase,
                                                                                         label_register_user,
                                                                                         button_back,
                                                                                         button_registrate,
                                                                                         progress_bar_authentication),
                                      width=width_275,
                                      height=height_70)
    button_registrate.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")


def button_registrate_phase_3_callback(label_third_phase, label_register_user, button_back, button_registrate,
                                       progress_bar_authentication):
    global new_user_unique_phrase, is_internet_connection, registration_with_internet

    button_repeat = ctk.CTkButton(master=frame_registrate_new_unique_phrase,
                                  text=Translations.get_translation('repeat'),
                                  font=(font_roboto, font_38, font_bold),
                                  command=button_repeat_phase_3_callback,
                                  width=width_275,
                                  height=height_70)

    button_confirm = ctk.CTkButton(master=frame_registrate_new_unique_phrase,
                                   text=Translations.get_translation('confirm'),
                                   font=(font_roboto, font_38, font_bold),
                                   command=lambda: button_confirm_phase_3_callback(label_register_user, button_repeat,
                                                                                   button_confirm),
                                   width=width_275,
                                   height=height_70)

    is_internet_connection = conn.check_internet_connection()

    if registration_with_internet and not is_internet_connection:
        registration_with_internet = is_internet_connection

    if is_internet_connection:
        label_third_phase.destroy()
        button_back.destroy()
        button_registrate.destroy()
        progress_bar_authentication.destroy()

        label_register_user.configure(text=Translations.get_translation('recording'),
                                      font=(font_roboto, font_38, font_bold), justify=ctk.CENTER)
        label_short_info = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                        text=Translations.get_translation(
                                            'short_info_3'),
                                        font=(font_roboto, font_38, font_bold), corner_radius=20, fg_color="#696969",
                                        justify=ctk.CENTER)
        label_short_info.grid(row=2, column=4, pady=10, padx=10, sticky="nsew")
        window.update()

        recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
        new_user_unique_phrase = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                               Translations.get_language().lower())
        new_user_unique_phrase = new_user_unique_phrase.lower()

        msg_info = f"Recognized new user unique phrase: {string_hasher.encode_string(new_user_unique_phrase)}"
        log.log_info(msg_info)

        label_register_user.configure(text=Translations.get_translation('recording_ended'))
        label_short_info.destroy()
        window.update()

        time.sleep(1.5)

        label_register_user.configure(text=Translations.get_translation('confirmation_phrase') + new_user_unique_phrase)

        button_repeat.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

        button_confirm.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

        window.update()
    else:
        frame_register_not_internet_callback("unique_phrase", label_register_user, button_repeat,
                                             button_confirm)


def button_repeat_phase_3_callback():
    frame_registrate_new_unique_phrase_callback()


def button_confirm_phase_3_callback(label_register_user, button_repeat, button_confirm):
    global new_user_nickname, new_user_unique_phrase, users, recordings_counter, is_internet_connection, registration_with_internet
    msg_info = f"New unique phrase {string_hasher.encode_string(new_user_unique_phrase)} registered successfully."
    log.log_info(msg_info)

    new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"

    if is_internet_connection:
        # VOICE RECOGNITION
        new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
        manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)

    recordings_counter = 0

    frame_register_not_internet.lower()
    clear_frame(frame_register_not_internet)
    clear_frame(frame_registrate_new_unique_phrase)
    label_register_user.destroy()
    button_repeat.destroy()
    button_confirm.destroy()
    window.update()

    label_registration_success = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                              text=Translations.get_translation('registration_success'),
                                              font=(font_roboto, font_38, font_bold), text_color=("light green"),
                                              justify=ctk.CENTER)
    label_registration_success.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

    label_processing = ctk.CTkLabel(master=frame_registrate_new_unique_phrase,
                                    text=Translations.get_translation(
                                        'processing_voiceprints'),
                                    font=(font_roboto, font_32), justify=ctk.CENTER)
    label_processing.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

    window.update()

    time.sleep(1.5)

    user_values = string_hasher.encode_string(new_user_unique_phrase) + (registration_with_internet,)

    if json.add_user_to_json_file(users, new_user_nickname,
                                  user_values,
                                  const.USERS_FILENAME):

        if not os.path.isdir(const.SPEAKER_VOICEPRINTS_DIR):
            os.mkdir(const.SPEAKER_VOICEPRINTS_DIR)

        output_dir = const.SPEAKER_VOICEPRINTS_DIR + new_user_nickname + "/"

        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        v_recognizer.create_voiceprints(classifier, new_user_dir, output_dir, const.NUMBER_OF_VOICEPRINTS + 2)

        if conn.check_internet_connection():
            db.insert_user_to_db(new_user_nickname)

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
    global is_internet_connection, is_admin_logged

    is_internet_connection = conn.check_internet_connection()

    clear_frame(frame_manage_users)
    frame_authentication_success.lower()
    frame_manage_users.lift()

    if is_internet_connection:
        users_to_show = users.copy()

        if not is_admin_logged:
            del users_to_show[currently_logged_user]

        label_main_title = ctk.CTkLabel(master=frame_manage_users,
                                        text=Translations.get_translation('system_authentication'),
                                        font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
        label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

        combobox_users = ctk.CTkComboBox(master=frame_manage_users, values=list(users_to_show.keys()),
                                         font=(font_roboto, font_38, font_bold),
                                         dropdown_font=(font_roboto, font_38, font_bold), justify=ctk.CENTER,
                                         hover=True,
                                         command=combobox_users_callback)
        combobox_users.grid(row=3, column=4, pady=10, padx=10, sticky="nsew")

        button_back = ctk.CTkButton(master=frame_manage_users, text=Translations.get_translation('back'),
                                    font=(font_roboto, font_38, font_bold),
                                    command=lambda: button_back_callback(frame_manage_users,
                                                                         frame_authentication_success),
                                    width=width_275,
                                    height=height_70)
        button_back.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

        button_delete_user = ctk.CTkButton(master=frame_manage_users,
                                           text=Translations.get_translation('delete'),
                                           font=(font_roboto, font_38, font_bold),
                                           command=button_delete_user_callback,
                                           width=width_275,
                                           height=height_70)
        button_delete_user.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")
    else:
        label_not_connection = ctk.CTkLabel(master=frame_manage_users,
                                            text=Translations.get_translation('internet'),
                                            font=(font_roboto, font_38, font_bold), text_color="red",
                                            justify=ctk.CENTER)
        label_not_connection.grid(row=3, column=4, sticky="nsew")
        window.update()

        time.sleep(1.5)

        button_back_callback(frame_manage_users, frame_authentication_success)


def combobox_users_callback(value):
    global user_to_delete
    user_to_delete = value


def button_delete_user_callback():
    global user_to_delete, users

    if conn.check_internet_connection():
        if user_to_delete in users.keys():
            if json.remove_user_from_json_file(users, user_to_delete, const.USERS_FILENAME):
                db.delete_user_from_db(user_to_delete)
                manager.remove_dir_with_files(const.SPEAKER_RECORDINGS_DIR + user_to_delete + "/")
                manager.remove_dir_with_files(const.SPEAKER_VOICEPRINTS_DIR + user_to_delete + "/")
                msg_info = f"User {user_to_delete} deleted successfully from the app database."
                log.log_info(msg_info)
            else:
                msg_warning = f"User {user_to_delete} not found in registered users."
                log.log_warning(msg_warning)
    else:
        msg_warning = f"User {user_to_delete} can't be deleted. Internet connection not available."
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

# create ADMIN FRAME
frame_admin = create_frame()
frame_admin.lower()

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
frame_registration = create_frame()
frame_registration.lower()
authentication_frames.append(frame_registration)

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
authentication_frames.append(frame_not_internet_connection)

# create NOT INTERNET NICKNAME FRAME
frame_register_not_internet = create_frame()
frame_register_not_internet.lower()
registration_frames.append(frame_register_not_internet)

# create INTRO FRAME widgets
label_main_title = ctk.CTkLabel(master=frame_intro, text=Translations.get_translation('system_authentication'),
                                font=(font_roboto, font_48, font_bold), justify=ctk.CENTER)
label_main_title.grid(row=1, column=4, pady=10, padx=10, sticky="nsew")

button_open_door = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('open_door'),
                                 font=(font_roboto, font_48, font_bold), command=button_open_door_callback)
button_open_door.grid(row=4, column=4, pady=10, padx=10, sticky="nsew")

button_about_project = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('about_project'),
                                     font=(font_roboto, font_38, font_bold), command=button_about_project_callback,
                                     width=width_150,
                                     height=height_50)
button_about_project.grid(row=7, column=7, pady=10, padx=10, sticky="nsew")

button_exit = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('exit'),
                            font=(font_roboto, font_38, font_bold),
                            command=button_exit_callback, width=width_150, height=height_50)
button_exit.grid(row=7, column=1, pady=10, padx=10, sticky="nsew")

segmented_button_language = ctk.CTkSegmentedButton(master=frame_intro, values=["SK", "EN"],
                                                   font=(font_roboto, font_38, font_bold),
                                                   command=segmented_button_language_callback, width=width_150,
                                                   height=height_50)
segmented_button_language.grid(row=6, column=7, pady=10, padx=10, sticky="nsew")

button_admin = ctk.CTkButton(master=frame_intro, text=Translations.get_translation('admin'),
                             font=(font_roboto, font_38, font_bold),
                             command=button_admin_callback, width=width_150, height=height_50, fg_color="#4a4a4a",
                             hover_color="#696969")
button_admin.grid(row=6, column=1, pady=10, padx=10, sticky="nsew")

is_internet_connection = conn.check_internet_connection()
users = json.load_json_file(const.USERS_FILENAME)
voiceprints_phrases = list(const.VOICEPRINT_PHRASES[Translations.get_language()])
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                            savedir=r"pretrained_models/spkrec-ecapa-voxceleb",
                                            run_opts={"device": "cpu"})

if conn.check_internet_connection():
    records = db.get_all_users_from_db()
    db_users = json.load_json_file(const.TMP_USERS_FILENAME)
    if users != db_users or list(users.keys()) != list(manager.get_subdirectory_names(const.SPEAKER_VOICEPRINTS_DIR)):
        db.sync_with_local()
    if os.path.isfile(const.TMP_USERS_FILENAME):
        os.remove(const.TMP_USERS_FILENAME)


def disable_minimize(event):
    window.overrideredirect(True)


window.bind("<Map>", disable_minimize)

window.mainloop()
