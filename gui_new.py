import os
import sys
import asyncio
import time

from PyQt6.QtWidgets import (QApplication,
                             QGridLayout,
                             QHBoxLayout,
                             QLabel,
                             QLineEdit,
                             QMainWindow,
                             QProgressBar,
                             QPushButton,
                             QStackedWidget,
                             QVBoxLayout,
                             QWidget)
from PyQt6.QtGui import QFont, QAction, QPixmap
from PyQt6.QtCore import Qt, QTimer
from qasync import QEventLoop
from speechbrain.pretrained import EncoderClassifier

from authentication import credentials, string_hasher
from database import json_file_builder as json
from database import connection_controller as conn
from database import db_operations as db
from general import constants as const
from general import log_file_builder as log
from general import file_manager as manager
from speech_and_voice import voice_recorder as recorder
from speech_and_voice import speech_recognizer as s_recognizer
from speech_and_voice import voice_recognizer as v_recognizer
from translations import Translations

index_intro_frame = 0
index_open_door_frame = 1
index_admin_frame = 2
index_about_frame = 3
index_sign_in_frame = 4
index_sign_up_frame = 5
index_auth_first_phase_frame = 6
index_not_internet_conn_frame = 7
index_auth_unsuccess_frame = 8


def initialize_font_sizes(window_width, window_height):
    fonts = [0, 0, 0]

    if window_width == 1920 and window_height == 1080:
        fonts[0] = const.FONT_LARGE
        fonts[1] = const.FONT_MEDIUM
        fonts[2] = const.FONT_SMALL
    elif window_width == 1280 and window_height == 720:
        fonts[0] = round(const.FONT_LARGE / 1.5)
        fonts[1] = round(const.FONT_MEDIUM / 1.5)
        fonts[2] = round(const.FONT_SMALL / 1.5)
    elif window_width > 1920 and window_height > 1080:
        fonts[0] = round(const.FONT_LARGE * 1.25)
        fonts[1] = round(const.FONT_MEDIUM * 1.25)
        fonts[2] = round(const.FONT_SMALL * 1.25)
    else:
        fonts[0] = round(const.FONT_LARGE / 2)
        fonts[1] = round(const.FONT_MEDIUM / 2)
        fonts[2] = round(const.FONT_SMALL / 2)

    return fonts


def initialize_image_sizes(window_width, window_height):
    rescaler = 0

    if window_width == 1920 and window_height == 1080:
        rescaler = const.IMAGE_RESCALER_FHD
    elif window_width == 1280 and window_height == 720:
        rescaler = const.IMAGE_RESCALER_HD
    elif window_width > 1920 and window_height > 1080:
        rescaler = const.IMAGE_RESCALER_FHD - 1
    else:
        rescaler = const.IMAGE_RESCALER_HD + 1

    return rescaler


def initialize_paddings_margins(pixels, window_width, window_height):
    resized_pixels = 0

    if window_width == 1920 and window_height == 1080:
        resized_pixels = pixels
    elif window_width == 1280 and window_height == 720:
        resized_pixels = round(pixels / 1.5)
    elif window_width > 1920 and window_height > 1080:
        resized_pixels = round(pixels * 1.25)
    else:
        resized_pixels = round(pixels / 2)

    return resized_pixels


def create_rows_cols(layout):
    layout.setRowStretch(0, 1)
    layout.setRowStretch(1, 1)
    layout.setRowStretch(2, 1)
    layout.setRowStretch(3, 1)
    layout.setRowStretch(4, 1)

    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 1)
    layout.setColumnStretch(2, 1)


class Frame(QWidget):
    def __init__(self):
        super().__init__()

        self.grid_layout = QGridLayout()
        create_rows_cols(self.grid_layout)

        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.grid_layout)

    def create_items(self):
        self.label_main_title = QLabel(Translations.get_translation("system_authentication"))
        self.label_main_title.setFont(QFont(const.FONT_RALEWAY_BOLD, font_large))
        self.label_main_title.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(self.label_main_title, 0, 1, Qt.AlignmentFlag.AlignCenter)

    def clear_items(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)
                self.grid_layout.removeItem(item)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_layout(child_layout)
                layout.removeItem(item)
        layout.deleteLater()


class IntroFrame(Frame):
    def __init__(self, switch_frames, update_menubar_items_translations):
        super().__init__()

        is_admin_logged = False

        self.switch_frames = switch_frames
        self.update_menubar_items_translations = update_menubar_items_translations

    def create_items(self):
        super().create_items()

        self.button_open_door = QPushButton(Translations.get_translation("open_door", True))
        self.button_open_door.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        self.button_open_door.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.button_open_door.clicked.connect(lambda: self.switch_frames(index_open_door_frame))
        self.grid_layout.addWidget(self.button_open_door, 2, 1, Qt.AlignmentFlag.AlignCenter)

        languages_layout = QHBoxLayout()

        button_sk = QPushButton("SK")
        button_en = QPushButton("EN")
        button_sk.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        button_en.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        if Translations.get_language() == "SK":
            button_sk.setEnabled(False)
        else:
            button_en.setEnabled(False)

        button_sk.setStyleSheet(
            f"padding: {btn_padding_t_b_20}px {btn_padding_l_r_30}px; margin: {btn_margin_0}px;")
        button_en.setStyleSheet(
            f"padding: {btn_padding_t_b_20}px {btn_padding_l_r_30}px; margin: {btn_margin_0}px;")

        button_sk.clicked.connect(lambda: self.change_language("SK", button_sk, button_en))
        button_sk.clicked.connect(lambda: self.update_menubar_items_translations())
        button_en.clicked.connect(lambda: self.change_language("EN", button_en, button_sk))
        button_en.clicked.connect(lambda: self.update_menubar_items_translations())

        languages_layout.addWidget(button_sk)
        languages_layout.addWidget(button_en)
        self.grid_layout.addLayout(languages_layout, 3, 1, Qt.AlignmentFlag.AlignCenter)

        image_label = QLabel()
        self.grid_layout.addWidget(image_label, 4, 1, Qt.AlignmentFlag.AlignCenter)
        image_pixmap = QPixmap("VAS - logo.png")
        scaled_pixmap = image_pixmap.scaled(round(image_pixmap.width() / rescale_factor),
                                            round(image_pixmap.height() / rescale_factor))
        image_label.setPixmap(scaled_pixmap)
        image_label.setStyleSheet(
            f"margin-top: {img_margin_40}px; margin-bottom: {img_margin_40}px;")

    def change_language(self, language, button_clicked, button_unclicked):
        Translations.set_language(language)
        button_clicked.setEnabled(False)
        button_unclicked.setEnabled(True)
        self.update_translations()

    def update_translations(self):
        self.label_main_title.setText(Translations.get_translation("system_authentication"))
        self.button_open_door.setText(Translations.get_translation("open_door", True))


class OpenDoorFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        sign_layout = QVBoxLayout()

        button_sign_in = QPushButton(Translations.get_translation("sign_in", True))
        button_sign_in.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_sign_in.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_sign_in.clicked.connect(lambda: self.switch_frames(index_sign_in_frame))

        button_sign_up = QPushButton(Translations.get_translation("sign_up", True))
        button_sign_up.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_sign_up.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_sign_up.clicked.connect(lambda: self.switch_frames(index_sign_up_frame))

        max_width = max(round(button_sign_in.width() / 2), round(button_sign_up.width() / 2))
        button_sign_in.setMinimumWidth(max_width)
        button_sign_up.setMinimumWidth(max_width)

        sign_layout.addWidget(button_sign_in)
        sign_layout.addWidget(button_sign_up)
        self.grid_layout.addLayout(sign_layout, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet("QPushButton:hover { background-color: #f47e21; }")
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_intro_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)


class AdminFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        label_admin_info = QLabel("\n\n" + Translations.get_translation("admin_interface"))
        label_admin_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_admin_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_admin_info.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_admin_info, 1, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_60}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_intro_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignLeft)

        entry_password = QLineEdit()
        entry_password.setEchoMode(QLineEdit.EchoMode.Password)
        entry_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        entry_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        entry_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.grid_layout.addWidget(entry_password, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_password = QPushButton(Translations.get_translation("confirm", True))
        button_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
        button_password.clicked.connect(lambda: self.verify_password(entry_password.text()))
        self.grid_layout.addWidget(button_password, 4, 2, Qt.AlignmentFlag.AlignRight)

    def verify_password(self, value):
        is_password_correct = string_hasher.check_string(value, credentials.admin_password,
                                                         credentials.admin_salt)

        if is_password_correct:
            is_admin_logged = True
            msg_success = "Entered password was correct."
            log.log_info(msg_success)
        else:
            msg_warning = "Entered password was incorrect."
            log.log_warning(msg_warning)


class AboutFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        label_about_project = QLabel("\t   " + Translations.get_translation("thesis", True) + "\n\n" +
                                     Translations.get_translation("topic_new") + "\n" +
                                     Translations.get_translation("student_new") + "\n" +
                                     Translations.get_translation("mentor_new") + "\n" +
                                     Translations.get_translation("year_new"))
        label_about_project.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_about_project.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label_about_project.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_about_project, 1, 1, Qt.AlignmentFlag.AlignJustify)

        label_school = QLabel(Translations.get_translation("university") + "\n\n" + Translations.get_translation(
            "faculty_new") + "\n\n" + Translations.get_translation("department_new"))
        label_school.setFont(QFont(const.FONT_RALEWAY_MEDIUM, round(font_small / 1.4)))
        label_school.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_school.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_school, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_60}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_intro_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignLeft)

        entry_password = QLineEdit()
        entry_password.setEchoMode(QLineEdit.EchoMode.Password)
        entry_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        entry_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        entry_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.grid_layout.addWidget(entry_password, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_password = QPushButton(Translations.get_translation("confirm", True))
        button_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
        button_password.clicked.connect(lambda: self.verify_password(entry_password.text()))
        self.grid_layout.addWidget(button_password, 4, 2, Qt.AlignmentFlag.AlignRight)

    def verify_password(self, value):
        is_password_correct = string_hasher.check_string(value, credentials.authentication_password,
                                                         credentials.authentication_salt)

        if is_password_correct and conn.check_internet_connection():
            msg_success = "Entered password was correct."
            log.log_info(msg_success)
        else:
            msg_warning = "Entered password was incorrect."
            log.log_warning(msg_warning)


class SignInFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        first_phase_layout = QVBoxLayout()

        label_first_phase = QLabel(Translations.get_translation("first_phase"))
        label_first_phase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_medium))
        label_first_phase.setStyleSheet(f"padding: {lbl_padding_20}px; color: #58a6d4;")
        label_first_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(False)
        progress_bar.setValue(round(100 / 3))
        progress_bar.setFixedSize(label_first_phase.width(), (2 * btn_padding_t_b_30))
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        first_phase_layout.addWidget(label_first_phase)
        first_phase_layout.addWidget(progress_bar)
        self.grid_layout.addLayout(first_phase_layout, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_authenticate_user = QLabel(
            "\n" + Translations.get_translation("come_closer_1") + "\n\n" + Translations.get_translation(
                "start_recording"))
        label_authenticate_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_authenticate_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_authenticate_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_authenticate_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_authenticate = QPushButton(Translations.get_translation("authenticate", True))
        button_authenticate.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_authenticate.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_authenticate.clicked.connect(lambda: self.switch_frames(index_auth_first_phase_frame))
        self.grid_layout.addWidget(button_authenticate, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_open_door_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)


class SignUpFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        label_registration_info = QLabel(
            "\n" + Translations.get_translation("registration_info") +
            "\n\n" + Translations.get_translation("continue_to_sign_in"))
        label_registration_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_registration_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_registration_info.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_registration_info, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_sign_in_again = QPushButton(Translations.get_translation("sign_in", True))
        button_sign_in_again.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_sign_in_again.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_sign_in_again.clicked.connect(lambda: self.switch_frames(index_sign_in_frame))
        self.grid_layout.addWidget(button_sign_in_again, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_open_door_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)


class AuthFirstPhaseFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        self.label_authenticate_user = QLabel(Translations.get_translation("recording"))
        self.label_authenticate_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        self.label_authenticate_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.label_authenticate_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(self.label_authenticate_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        if not conn.quick_check_internet_connection():
            asyncio.create_task(self.quick_check_internet_conn())
            return

        label_short_info = QLabel(Translations.get_translation("short_info_1"))
        label_short_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        label_short_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_short_info.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #f47e21; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_short_info, 1, 1, Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.verify_speaker_name())

    async def quick_check_internet_conn(self):
        timeout = 10
        start_time = time.time()

        while not conn.quick_check_internet_connection():
            self.label_authenticate_user.setText(Translations.get_translation("waiting_for_connection"))
            if time.time() - start_time >= timeout:
                break
            await asyncio.sleep(0.5)

        if conn.quick_check_internet_connection():
            self.clear_items()
            self.create_items()
        else:
            self.switch_frames(index_not_internet_conn_frame)

    async def verify_speaker_name(self):
        global currently_logged_user, partial_authentication

        await asyncio.sleep(0.5)
        recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME)
        speaker_nickname = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                         Translations.get_language().lower())
        speaker_nickname = speaker_nickname.lower()
        speaker_exists = s_recognizer.verify_speaker_nickname(users.keys(), speaker_nickname)

        msg_info = f"Recognized speaker nickname: {speaker_nickname}"
        log.log_info(msg_info)

        self.label_authenticate_user.setText(Translations.get_translation("recording_ended"))

        time.sleep(1.5)

        if speaker_exists:
            currently_logged_user = speaker_nickname

            if s_recognizer.user_registered_with_internet(users, currently_logged_user):
                speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + speaker_nickname + "/"
                login_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                           const.RECORDED_AUDIO_FILENAME,
                                                                           auth_weight=10)
                partial_authentication = partial_authentication + score
            else:
                login_success = speaker_exists

            if login_success:
                msg_success = f"User {speaker_nickname} signed in successfully."
                log.log_info(msg_success)
                self.switch_frames(index_intro_frame)
            else:
                msg_warning = f"User {speaker_nickname} failed to sign in. Voice characteristics don't match."
                log.log_warning(msg_warning)
                self.switch_frames(index_auth_unsuccess_frame)
        else:
            msg_warning = f"Speaker {speaker_nickname} does not exist. "
            log.log_warning(msg_warning)
            self.switch_frames(index_auth_unsuccess_frame)


class NotInternetConnFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        label_not_connection = QLabel(Translations.get_translation("internet", True))
        label_not_connection.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        label_not_connection.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_not_connection.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_not_connection, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_limited_mode = QLabel(Translations.get_translation("limited_mode") +
                                    "\n\n" + Translations.get_translation("password_to_continue"))
        label_limited_mode.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_limited_mode.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_limited_mode.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_limited_mode, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_60}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_sign_in_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignLeft)

        entry_password = QLineEdit()
        entry_password.setEchoMode(QLineEdit.EchoMode.Password)
        entry_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        entry_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        entry_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.grid_layout.addWidget(entry_password, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_password = QPushButton(Translations.get_translation("confirm", True))
        button_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
        button_password.clicked.connect(lambda: self.verify_password(entry_password.text()))
        self.grid_layout.addWidget(button_password, 4, 2, Qt.AlignmentFlag.AlignRight)

    def verify_password(self, value):
        is_password_correct = string_hasher.check_string(value, credentials.authentication_password,
                                                         credentials.authentication_salt)

        if is_password_correct and conn.check_internet_connection():
            msg_success = "Entered password was correct."
            log.log_info(msg_success)
        else:
            msg_warning = "Entered password was incorrect."
            log.log_warning(msg_warning)


class AuthUnsuccessFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        self.verify_remaining_attempts()

        label_authentication_unsuccess = QLabel(Translations.get_translation("authentication_unsuccess", True))
        label_authentication_unsuccess.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_medium))
        label_authentication_unsuccess.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_authentication_unsuccess.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4;; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_authentication_unsuccess, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_authentication_unsuccess_info = QLabel(Translations.get_translation("authentication_unsuccess_info") +
                                    "\n\n" + Translations.get_translation("remaining_attempts") +
                                    str(remaining_attempts) +
                                    "\n\n" + Translations.get_translation("start_authentication_again")                 )
        label_authentication_unsuccess_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_authentication_unsuccess_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_authentication_unsuccess_info.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_authentication_unsuccess_info, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_authenticate_again = QPushButton(Translations.get_translation("authenticate_again", True))
        button_authenticate_again.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_authenticate_again.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_authenticate_again.clicked.connect(lambda: self.switch_frames(index_auth_first_phase_frame, 1))
        self.grid_layout.addWidget(button_authenticate_again, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_sign_in_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)

    def verify_remaining_attempts(self):
        global remaining_attempts
        remaining_attempts -= 1

        msg_warning = f"Error during authentication process. Remaining attempts: {remaining_attempts}"
        log.log_warning(msg_warning)

        if remaining_attempts == 0:
            remaining_attempts = 3
            self.switch_frames(index_intro_frame)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showFullScreen()

        self.menu_bar = None

        self.initialize_screen_resolution()

        self.setWindowTitle(Translations.get_translation("system_authentication"))

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.intro_frame = IntroFrame(self.switch_frame, self.update_menubar_items_translations)
        self.open_door_frame = OpenDoorFrame(self.switch_frame)
        self.admin_frame = AdminFrame(self.switch_frame)
        self.about_frame = AboutFrame(self.switch_frame)
        self.sign_in_frame = SignInFrame(self.switch_frame)
        self.sign_up_frame = SignUpFrame(self.switch_frame)
        self.auth_first_phase_frame = AuthFirstPhaseFrame(self.switch_frame)
        self.not_internet_conn_frame = NotInternetConnFrame(self.switch_frame)
        self.auth_unsuccess_frame = AuthUnsuccessFrame(self.switch_frame)

        self.stacked_widget.addWidget(self.intro_frame)
        self.stacked_widget.addWidget(self.open_door_frame)
        self.stacked_widget.addWidget(self.admin_frame)
        self.stacked_widget.addWidget(self.about_frame)
        self.stacked_widget.addWidget(self.sign_in_frame)
        self.stacked_widget.addWidget(self.sign_up_frame)
        self.stacked_widget.addWidget(self.auth_first_phase_frame)
        self.stacked_widget.addWidget(self.not_internet_conn_frame)
        self.stacked_widget.addWidget(self.auth_unsuccess_frame)

        self.intro_frame.create_items()
        self.create_menu()
        self.apply_styles()

    def create_menu(self):
        self.menu_bar = self.menuBar()
        self.menu_bar.setFont(QFont(const.FONT_RHD_MEDIUM, font_small))

        intro_action = QAction(Translations.get_translation("intro"), self)
        intro_action.triggered.connect(lambda: self.switch_frame(index_intro_frame))

        about_action = QAction(Translations.get_translation("about_project"), self)
        about_action.triggered.connect(lambda: self.switch_frame(index_about_frame))

        admin_action = QAction(Translations.get_translation("admin"), self)
        admin_action.triggered.connect(lambda: self.switch_frame(index_admin_frame))

        exit_action = QAction(Translations.get_translation("exit"), self)
        exit_action.triggered.connect(lambda: sys.exit())

        self.menu_bar.addActions([intro_action, about_action, admin_action, exit_action])

    def update_menubar_items_translations(self):
        self.setWindowTitle(Translations.get_translation("system_authentication"))
        self.menu_bar.actions()[0].setText(Translations.get_translation("intro"))
        self.menu_bar.actions()[1].setText(Translations.get_translation("about_project"))
        self.menu_bar.actions()[2].setText(Translations.get_translation("admin"))
        self.menu_bar.actions()[3].setText(Translations.get_translation("exit"))

    """
        indexes:
            0 - intro_frame
            1 - open_door_frame
            2 - admin_frame
            3 - about_frame
            4 - sign_in_frame
            5 - sign_up_frame
            6 - auth_first_phase_frame
    """

    def switch_frame(self, index, auth_phase=None):
        if auth_phase is not None:
            if auth_phase == 1:
                index = index_auth_first_phase_frame
            if auth_phase == 2:
                #index = index_auth_second_phase_frame
                return
            if auth_phase == 3:
                #index = index_auth_third_phase_frame
                return

        self.stacked_widget.currentWidget().clear_items()
        self.stacked_widget.currentWidget().destroy()
        self.stacked_widget.setCurrentIndex(index)
        self.stacked_widget.currentWidget().create_items()

    """
        color palette:
            orange - #f47e21
            blue - #58a6d4
            light blue - #a2d5ec
            black - #000000
            white - #ffffff
    """

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #a2d5ec;
            }}
            QMenuBar {{
                background-color: #58a6d4;
                color: #000000;
            }}
            QMenuBar::item {{
                padding: {btn_padding_t_b_30}px {btn_padding_l_r_40}px;
                margin: {btn_margin_0}px {btn_margin_20}px;
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: #f47e21;
                color: #000000;
                border-radius: {border_radius_15}px;
                border: {border_width_5}px solid #000000;
            }}
            QPushButton {{
                background-color: #f47e21;
                color: #000000;
                border-radius: {border_radius_15}px;
                border: {border_width_5}px solid #000000;
            }}
            QPushButton:hover {{
                background-color: #58a6d4;
            }}
            QPushButton:disabled {{
                background-color: #58a6d4;
            }}
            QLabel {{
                color: #000000; 
            }}
            QLineEdit {{
                background-color: #58a6d4;
                color: #000000;
                border-radius: {border_radius_15}px;
                border: {border_width_5}px solid #000000;
            }}
            QProgressBar {{
                background-color: #a2d5ec;
                border-radius: {border_radius_15}px;
                border: {border_width_5}px solid #000000;
            }}
            QProgressBar::chunk {{
                background-color: #58a6d4;
                border-radius: {border_radius_10}px;
            }}
        """)

    def initialize_screen_resolution(self):
        global font_large, font_medium, font_small
        global rescale_factor
        global btn_padding_t_b_20, btn_padding_t_b_30, btn_padding_t_b_60
        global btn_padding_l_r_30, btn_padding_l_r_40, btn_padding_l_r_60, btn_padding_l_r_80
        global btn_margin_0, btn_margin_20
        global lbl_padding_10, lbl_padding_20
        global img_margin_30, img_margin_40
        global border_width_5, border_radius_10, border_radius_15

        font_sizes = initialize_font_sizes(self.size().width(), self.size().height())
        font_large, font_medium, font_small = font_sizes[0], font_sizes[1], font_sizes[2]

        rescale_factor = initialize_image_sizes(self.size().width(), self.size().height())

        btn_padding_t_b_20 = initialize_paddings_margins(const.BTN_PADDING_T_B_20, self.size().width(),
                                                         self.size().height())
        btn_padding_t_b_30 = initialize_paddings_margins(const.BTN_PADDING_T_B_30, self.size().width(),
                                                         self.size().height())
        btn_padding_t_b_60 = initialize_paddings_margins(const.BTN_PADDING_T_B_60, self.size().width(),
                                                         self.size().height())
        btn_padding_l_r_30 = initialize_paddings_margins(const.BTN_PADDING_L_R_30, self.size().width(),
                                                         self.size().height())
        btn_padding_l_r_40 = initialize_paddings_margins(const.BTN_PADDING_L_R_40, self.size().width(),
                                                         self.size().height())
        btn_padding_l_r_60 = initialize_paddings_margins(const.BTN_PADDING_L_R_60, self.size().width(),
                                                         self.size().height())
        btn_padding_l_r_80 = initialize_paddings_margins(const.BTN_PADDING_L_R_80, self.size().width(),
                                                         self.size().height())
        btn_margin_0 = initialize_paddings_margins(const.BTN_MARGIN_0, self.size().width(),
                                                   self.size().height())
        btn_margin_20 = initialize_paddings_margins(const.BTN_MARGIN_20, self.size().width(),
                                                    self.size().height())
        lbl_padding_10 = initialize_paddings_margins(const.LBL_PADDING_10, self.size().width(),
                                                     self.size().height())
        lbl_padding_20 = initialize_paddings_margins(const.LBL_PADDING_20, self.size().width(),
                                                     self.size().height())
        img_margin_30 = initialize_paddings_margins(const.IMG_MARGIN_30, self.size().width(),
                                                    self.size().height())
        img_margin_40 = initialize_paddings_margins(const.IMG_MARGIN_40, self.size().width(),
                                                    self.size().height())
        border_width_5 = initialize_paddings_margins(const.BORDER_WIDTH_5, self.size().width(),
                                                     self.size().height())
        border_radius_10 = initialize_paddings_margins(const.BORDER_RADIUS_10, self.size().width(),
                                                       self.size().height())
        border_radius_15 = initialize_paddings_margins(const.BORDER_RADIUS_15, self.size().width(),
                                                       self.size().height())


currently_logged_user = ""
partial_authentication = 0.0
remaining_attempts = 3
is_admin_logged = False
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()
