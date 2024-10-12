import os
import sys
import asyncio
import time
import argparse

from PyQt6.QtWidgets import (QApplication,
                             QComboBox,
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
from PyQt6.QtCore import Qt
from qasync import QEventLoop, asyncSlot
from speechbrain.inference import EncoderClassifier

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


index_intro_frame = const.INDEX_INTRO_FRAME
index_open_door_frame = const.INDEX_OPEN_DOOR_FRAME
index_admin_frame = const.INDEX_ADMIN_FRAME
index_about_frame = const.INDEX_ABOUT_FRAME
index_sign_in_frame = const.INDEX_SIGN_IN_FRAME
index_sign_up_frame = const.INDEX_SIGN_UP_FRAME
index_first_phase_success_frame = const.INDEX_FIRST_PHASE_SUCCESS_FRAME
index_second_phase_success_frame = const.INDEX_SECOND_PHASE_SUCCESS_FRAME
index_auth_first_phase_frame = const.INDEX_AUTH_FIRST_PHASE_FRAME
index_auth_second_phase_frame = const.INDEX_AUTH_SECOND_PHASE_FRAME
index_auth_third_phase_frame = const.INDEX_AUTH_THIRD_PHASE_FRAME
index_not_internet_conn_frame = const.INDEX_NOT_INTERNET_CONN_FRAME
index_auth_unsuccess_frame = const.INDEX_AUTH_UNSUCCESS_FRAME
index_auth_success_frame = const.INDEX_AUTH_SUCCESS_FRAME
index_register_frame = const.INDEX_REGISTER_FRAME
index_reg_first_phase_completed_frame = const.INDEX_REG_FIRST_PHASE_COMPLETED_FRAME
index_reg_second_phase_completed_frame = const.INDEX_REG_SECOND_PHASE_COMPLETED_FRAME
index_reg_first_phase_frame = const.INDEX_REG_FIRST_PHASE_FRAME
index_reg_second_phase_frame = const.INDEX_REG_SECOND_PHASE_FRAME
index_reg_third_phase_frame = const.INDEX_REG_THIRD_PHASE_FRAME
index_reg_not_internet_conn_frame = const.INDEX_REG_NOT_INTERNET_CONN_FRAME
index_reg_success_frame = const.INDEX_REG_SUCCESS_FRAME
index_manage_users = const.INDEX_MANAGE_USERS


def clear_global_variables():
    global simple_mode, skip_auth_info, is_admin_logged, registration_with_internet, currently_logged_user, user_to_delete, \
        new_user_nickname, new_user_unique_phrase, index_to_return, index_to_repeat, voiceprints_counter, \
        recordings_counter, remaining_attempts, partial_authentication
    simple_mode = False
    skip_auth_info = False
    is_admin_logged = False
    registration_with_internet = True
    currently_logged_user = ""
    user_to_delete = ""
    new_user_nickname = ""
    new_user_unique_phrase = ""
    index_to_return = -1
    index_to_repeat = -1
    voiceprints_counter = 0
    recordings_counter = 0
    remaining_attempts = 3
    partial_authentication = 0.0


def initialize_font_sizes(window_width, window_height):
    fonts = [0, 0, 0, 0]

    if window_width == 1920 and window_height == 1080:
        fonts[0] = const.FONT_LARGE
        fonts[1] = const.FONT_MEDIUM
        fonts[2] = const.FONT_SMALL_MEDIUM
        fonts[3] = const.FONT_SMALL
    elif window_width == 1280 and window_height == 720:
        fonts[0] = round(const.FONT_LARGE / 1.5)
        fonts[1] = round(const.FONT_MEDIUM / 1.5)
        fonts[2] = round(const.FONT_SMALL_MEDIUM / 1.5)
        fonts[3] = round(const.FONT_SMALL / 1.5)
    elif window_width == 960 and window_height == 540:
        fonts[0] = round(const.FONT_LARGE / 2.1)
        fonts[1] = round(const.FONT_MEDIUM / 2.1)
        fonts[2] = round(const.FONT_SMALL_MEDIUM / 2.1)
        fonts[3] = round(const.FONT_SMALL / 2.1)
    elif window_width > 1920 and window_height > 1080:
        fonts[0] = round(const.FONT_LARGE * 1.25)
        fonts[1] = round(const.FONT_MEDIUM * 1.25)
        fonts[2] = round(const.FONT_SMALL_MEDIUM / 1.25)
        fonts[3] = round(const.FONT_SMALL * 1.25)
    else:
        fonts[0] = round(const.FONT_LARGE / 2)
        fonts[1] = round(const.FONT_MEDIUM / 2)
        fonts[2] = round(const.FONT_SMALL_MEDIUM / 2)
        fonts[3] = round(const.FONT_SMALL / 2)

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
    elif window_width == 960 and window_height == 540:
        resized_pixels = round(pixels / 2.1)
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

        self.switch_frames = switch_frames
        self.update_menubar_items_translations = update_menubar_items_translations

    def create_items(self):
        global is_admin_logged

        super().create_items()

        is_admin_logged = False

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

        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        self.entry_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.grid_layout.addWidget(self.entry_password, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_password = QPushButton(Translations.get_translation("confirm", True))
        button_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
        button_password.clicked.connect(lambda: self.verify_password(self.entry_password.text()))
        self.grid_layout.addWidget(button_password, 4, 2, Qt.AlignmentFlag.AlignRight)

    @asyncSlot()
    async def verify_password(self, value):
        global is_admin_logged

        is_password_correct = string_hasher.check_string(value, credentials.admin_password,
                                                         credentials.admin_salt)

        if is_password_correct:
            is_admin_logged = True
            msg_success = "Entered password was correct."
            log.log_info(msg_success)
            self.switch_frames(index_auth_success_frame)
        else:
            msg_warning = "Entered password was incorrect."
            log.log_warning(msg_warning)
            self.entry_password.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px; "
                f"border: {border_width_5}px solid #f47e21;")
            await asyncio.sleep(1)
            self.entry_password.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px; "
                f"border: {border_width_5}px solid #000000;")


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

        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        self.entry_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.grid_layout.addWidget(self.entry_password, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_password = QPushButton(Translations.get_translation("confirm", True))
        button_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
        button_password.clicked.connect(lambda: self.verify_password(self.entry_password.text()))
        self.grid_layout.addWidget(button_password, 4, 2, Qt.AlignmentFlag.AlignRight)

    @asyncSlot()
    async def verify_password(self, value):
        is_password_correct = string_hasher.check_string(value, credentials.authentication_password,
                                                         credentials.authentication_salt)

        if is_password_correct:
            msg_success = "Entered password was correct."
            log.log_info(msg_success)
            self.switch_frames(index_second_phase_success_frame)
        else:
            msg_warning = "Entered password was incorrect."
            log.log_warning(msg_warning)
            self.entry_password.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px; "
                f"border: {border_width_5}px solid #f47e21;")
            await asyncio.sleep(1)
            self.entry_password.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px; "
                f"border: {border_width_5}px solid #000000;")


class SignInFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        global simple_mode

        first_phase_layout = QVBoxLayout()

        label_first_phase = QLabel(Translations.get_translation("first_phase"))
        label_first_phase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_medium))
        label_first_phase.setStyleSheet(f"padding: {lbl_padding_20}px; color: #58a6d4;")
        label_first_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(False)
        progress_bar.setValue(round(100 / 3))
        if simple_mode is True:
            progress_bar.setValue(round(100 / 2))
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


class FirstPhaseSuccess(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    @asyncSlot()
    async def create_items(self):
        super().create_items()

        label_sign_in_success = QLabel(Translations.get_translation("sign_in_success", True))
        label_sign_in_success.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_sign_in_success.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_sign_in_success.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_sign_in_success, 1, 1, Qt.AlignmentFlag.AlignCenter)

        await asyncio.sleep(2)

        label_sign_in_success.setHidden(True)

        second_phase_layout = QVBoxLayout()

        label_second_phase = QLabel(Translations.get_translation("second_phase"))
        label_second_phase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_medium))
        label_second_phase.setStyleSheet(f"padding: {lbl_padding_20}px; color: #58a6d4;")
        label_second_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(False)
        progress_bar.setValue(round((100 / 3) * 2))
        progress_bar.setFixedSize(label_second_phase.width(), (2 * btn_padding_t_b_30))
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        second_phase_layout.addWidget(label_second_phase)
        second_phase_layout.addWidget(progress_bar)
        self.grid_layout.addLayout(second_phase_layout, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_authenticate_user = QLabel(
            "\n" + Translations.get_translation("come_closer_2") + "\n\n" + Translations.get_translation(
                "start_recording"))
        label_authenticate_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_authenticate_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_authenticate_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_authenticate_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_authenticate = QPushButton(Translations.get_translation("authenticate", True))
        button_authenticate.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_authenticate.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_authenticate.clicked.connect(lambda: self.switch_frames(index_auth_second_phase_frame))
        self.grid_layout.addWidget(button_authenticate, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_sign_in_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)


class SecondPhaseSuccess(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    @asyncSlot()
    async def create_items(self):
        super().create_items()

        global simple_mode

        label_verification_success = QLabel(Translations.get_translation("verification_success", True))
        label_verification_success.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_verification_success.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_verification_success.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_verification_success, 1, 1, Qt.AlignmentFlag.AlignCenter)

        await asyncio.sleep(2)

        label_verification_success.setHidden(True)

        third_phase_layout = QVBoxLayout()

        label_third_phase = QLabel(Translations.get_translation("third_phase"))
        if simple_mode is True:
            label_third_phase = QLabel(Translations.get_translation("second_phase"))
        label_third_phase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_medium))
        label_third_phase.setStyleSheet(f"padding: {lbl_padding_20}px; color: #58a6d4;")
        label_third_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(False)
        progress_bar.setValue(100)
        progress_bar.setFixedSize(label_third_phase.width(), (2 * btn_padding_t_b_30))
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        third_phase_layout.addWidget(label_third_phase)
        third_phase_layout.addWidget(progress_bar)
        self.grid_layout.addLayout(third_phase_layout, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_authenticate_user = QLabel(
            "\n" + Translations.get_translation("come_closer_3") + "\n\n" + Translations.get_translation(
                "start_recording"))
        label_authenticate_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_authenticate_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_authenticate_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_authenticate_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_authenticate = QPushButton(Translations.get_translation("authenticate", True))
        button_authenticate.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_authenticate.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_authenticate.clicked.connect(lambda: self.switch_frames(index_auth_third_phase_frame))
        self.grid_layout.addWidget(button_authenticate, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        if simple_mode is False:
            button_back.clicked.connect(lambda: self.switch_frames(index_first_phase_success_frame))
        else:
            button_back.clicked.connect(lambda: self.switch_frames(index_sign_in_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)


class AuthFirstPhaseFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global index_to_return, index_to_repeat
        index_to_return = index_sign_in_frame
        index_to_repeat = index_auth_first_phase_frame

        super().create_items()

        self.label_authenticate_user = QLabel(Translations.get_translation("recording"))
        self.label_authenticate_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_authenticate_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.label_authenticate_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(self.label_authenticate_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        if not conn.quick_check_internet_connection():
            asyncio.create_task(self.quick_check_internet_conn())
            return

        label_short_info = QLabel(Translations.get_translation("short_info_1"))
        label_short_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
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
        global currently_logged_user, partial_authentication, simple_mode

        await asyncio.sleep(0.5)

        if recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME):
            speaker_nickname = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                             Translations.get_language().lower())
            speaker_nickname = speaker_nickname.lower()
            speaker_exists = s_recognizer.verify_speaker_nickname(users.keys(), speaker_nickname)

            msg_info = f"Recognized speaker nickname: {speaker_nickname}"
            log.log_info(msg_info)

            self.label_authenticate_user.setText(Translations.get_translation("recording_ended"))

            await asyncio.sleep(2)

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
                    if simple_mode is False:
                        self.switch_frames(index_first_phase_success_frame)
                    else:
                        self.switch_frames(index_second_phase_success_frame)
                else:
                    msg_warning = f"User {speaker_nickname} failed to sign in. Voice characteristics don't match."
                    log.log_warning(msg_warning)
                    self.switch_frames(index_auth_unsuccess_frame)
            else:
                msg_warning = f"Speaker {speaker_nickname} does not exist."
                log.log_warning(msg_warning)
                self.switch_frames(index_auth_unsuccess_frame)
        else:
            msg_error = f"Recording was not created. Please check your microphone settings."
            log.log_warning(msg_error)
            self.switch_frames(index_auth_unsuccess_frame)


class AuthSecondPhaseFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global index_to_return, index_to_repeat
        index_to_return = index_first_phase_success_frame
        index_to_repeat = index_auth_second_phase_frame

        super().create_items()

        self.label_authenticate_user = QLabel(Translations.get_translation("recording"))
        self.label_authenticate_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_authenticate_user.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_authenticate_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(self.label_authenticate_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        if not conn.quick_check_internet_connection():
            asyncio.create_task(self.quick_check_internet_conn())
            return

        labels_layout = QVBoxLayout()

        label_short_info = QLabel(Translations.get_translation("short_info_2"))
        label_short_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_short_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_short_info.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #f47e21; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_short_info, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.random_word = s_recognizer.generate_random_word(const.VERIFICATION_WORDS[Translations.get_language()])

        self.label_random_word = QLabel("\n" + self.random_word.upper() + "\n")
        self.label_random_word.setFont(QFont(const.FONT_RALEWAY_BOLD, font_small))
        self.label_random_word.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_random_word.setStyleSheet(f"padding: {lbl_padding_20}px; word-spacing: {lbl_padding_10}px; font-style: italic;")

        labels_layout.addWidget(self.label_random_word)
        labels_layout.addWidget(self.label_authenticate_user)
        self.grid_layout.addLayout(labels_layout, 2, 1, Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.verify_spoken_word())

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

    async def verify_spoken_word(self):
        global partial_authentication

        await asyncio.sleep(0.5)

        if recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME):
            spoken_verification_word = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                                     Translations.get_language().lower())
            spoken_verification_word_matches = s_recognizer.verify_verification_word(spoken_verification_word, self.random_word)

            msg_info = f"Recognized verification word: {spoken_verification_word}"
            log.log_info(msg_info)

            self.label_authenticate_user.setText(Translations.get_translation("recording_ended"))
            self.label_random_word.setHidden(True)

            await asyncio.sleep(2)

            if spoken_verification_word_matches:

                speaker_dir = const.SPEAKER_VOICEPRINTS_DIR + currently_logged_user + "/"
                verification_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                                  const.RECORDED_AUDIO_FILENAME,
                                                                                  auth_weight=20)
                partial_authentication = partial_authentication + score

                if verification_success:
                    msg_success = f"Verification word {self.random_word} matched with spoken word {spoken_verification_word}. Speaker is registered user."
                    log.log_info(msg_success)
                    self.switch_frames(index_second_phase_success_frame)
                else:
                    msg_warning = f"Speaker's voice characteristics don't match."
                    log.log_warning(msg_warning)
                    self.switch_frames(index_auth_unsuccess_frame)
            else:
                msg_warning = f"Verification word {self.random_word} didn't match with spoken word {spoken_verification_word}."
                log.log_warning(msg_warning)
                self.switch_frames(index_auth_unsuccess_frame)
        else:
            msg_error = f"Recording was not created. Please check your microphone settings."
            log.log_warning(msg_error)
            self.switch_frames(index_auth_unsuccess_frame)


class AuthThirdPhaseFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames
        self.internet_checked = False

    def create_items(self):
        global index_to_return, index_to_repeat
        index_to_return = index_second_phase_success_frame
        index_to_repeat = index_auth_third_phase_frame

        super().create_items()

        self.label_authenticate_user = QLabel(Translations.get_translation("recording"))
        self.label_authenticate_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_authenticate_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.label_authenticate_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(self.label_authenticate_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        if not conn.quick_check_internet_connection() and self.internet_checked is False:
            asyncio.create_task(self.quick_check_internet_conn())
            return

        label_short_info = QLabel(Translations.get_translation("short_info_3"))
        label_short_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_short_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_short_info.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #f47e21; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_short_info, 1, 1, Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.verify_unique_phrase())

    async def quick_check_internet_conn(self):
        self.internet_checked = False
        timeout = 5
        start_time = time.time()

        while not conn.quick_check_internet_connection():
            self.label_authenticate_user.setText(Translations.get_translation("waiting_for_connection"))
            if time.time() - start_time >= timeout:
                break
            await asyncio.sleep(0.5)

        self.internet_checked = True
        self.clear_items()
        self.create_items()

    async def verify_unique_phrase(self):
        global currently_logged_user, partial_authentication, simple_mode
        skipped_phases = False

        await asyncio.sleep(0.5)

        if recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME):
            if conn.quick_check_internet_connection():
                unique_phrase = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                              Translations.get_language().lower())
                unique_phrase = unique_phrase.lower()
                unique_phrase_matches = s_recognizer.verify_unique_phrase(users, currently_logged_user, unique_phrase)
            else:
                unique_phrase = ""
                unique_phrase_matches = True

            self.label_authenticate_user.setText(Translations.get_translation("recording_ended"))

            await asyncio.sleep(2)

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

                    if not skipped_phases:
                        if not simple_mode:
                            authentication_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                                                const.RECORDED_AUDIO_FILENAME,
                                                                                                auth_weight=70)
                        else:
                            authentication_success, score = v_recognizer.verify_speaker_concept(classifier, speaker_dir,
                                                                                                const.RECORDED_AUDIO_FILENAME,
                                                                                                auth_weight=90)
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
                            self.switch_frames(index_auth_success_frame)
                        else:
                            msg_warning = f"Final result of partial authentication is under the threshold."
                            log.log_warning(msg_warning)
                            partial_authentication = partial_authentication - score
                            self.switch_frames(index_auth_unsuccess_frame)
                    else:
                        msg_warning = f"Speaker's voice characteristics don't match. Door can't be opened."
                        log.log_warning(msg_warning)
                        self.switch_frames(index_auth_unsuccess_frame)
                else:
                    msg_warning = f"Speaker's voice characteristics don't correspond with his unique phrase."
                    log.log_warning(msg_warning)
                    self.switch_frames(index_auth_unsuccess_frame)
            else:
                msg_warning = f"Authentication with unique phrase wasn't successful. User {currently_logged_user} couldn't open the door."
                log.log_warning(msg_warning)
                self.switch_frames(index_auth_unsuccess_frame)
        else:
            msg_error = f"Recording was not created. Please check your microphone settings."
            log.log_warning(msg_error)
            self.switch_frames(index_auth_unsuccess_frame)


class NotInternetConnFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global index_to_return

        super().create_items()

        label_not_connection = QLabel(Translations.get_translation("internet", True))
        label_not_connection.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
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
        button_back.clicked.connect(lambda: self.switch_frames(index_to_return))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignLeft)

        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        self.entry_password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.grid_layout.addWidget(self.entry_password, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_password = QPushButton(Translations.get_translation("confirm", True))
        button_password.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_password.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
        button_password.clicked.connect(lambda: self.verify_password(self.entry_password.text()))
        self.grid_layout.addWidget(button_password, 4, 2, Qt.AlignmentFlag.AlignRight)

    @asyncSlot()
    async def verify_password(self, value):
        is_password_correct = string_hasher.check_string(value, credentials.authentication_password,
                                                         credentials.authentication_salt)

        if is_password_correct:
            msg_success = "Entered password was correct."
            log.log_info(msg_success)
            self.switch_frames(index_second_phase_success_frame)
        else:
            msg_warning = "Entered password was incorrect."
            log.log_warning(msg_warning)
            self.entry_password.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px; "
                f"border: {border_width_5}px solid #f47e21;")
            await asyncio.sleep(1)
            self.entry_password.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px; "
                f"border: {border_width_5}px solid #000000;")


class AuthUnsuccessFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global index_to_return, index_to_repeat

        super().create_items()

        self.verify_remaining_attempts()

        label_authentication_unsuccess = QLabel(Translations.get_translation("authentication_unsuccess", True))
        label_authentication_unsuccess.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
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
        button_authenticate_again.clicked.connect(lambda: self.switch_frames(index_to_repeat))
        self.grid_layout.addWidget(button_authenticate_again, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_to_return))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)

    def verify_remaining_attempts(self):
        global remaining_attempts
        remaining_attempts -= 1

        msg_warning = f"Error during authentication process. Remaining attempts: {remaining_attempts}"
        log.log_warning(msg_warning)

        if remaining_attempts == 0:
            remaining_attempts = 3
            self.switch_frames(index_intro_frame)


class AuthSuccessFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    @asyncSlot()
    async def create_items(self):
        global remaining_attempts, currently_logged_user, skip_auth_info, is_admin_logged
        remaining_attempts = 3

        super().create_items()

        if not skip_auth_info:
            label_authentication_success = QLabel(Translations.get_translation("authentication_success", True))
            label_authentication_success.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
            label_authentication_success.setAlignment(Qt.AlignmentFlag.AlignJustify)
            label_authentication_success.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
                f"border-radius: {border_radius_15};")
            self.grid_layout.addWidget(label_authentication_success, 1, 1, Qt.AlignmentFlag.AlignCenter)

            await asyncio.sleep(2)

            label_authentication_success.setHidden(True)

        skip_auth_info = True

        if is_admin_logged:
            currently_logged_user = "admin"

        label_logged_user = QLabel(Translations.get_translation('logged_user', True) + currently_logged_user)
        label_logged_user.setFont(QFont(const.FONT_RALEWAY_BOLD, font_small))
        label_logged_user.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_logged_user.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
            f"border-radius: {border_radius_15}; word-spacing: {lbl_padding_10}px;")
        self.grid_layout.addWidget(label_logged_user, 1, 1, Qt.AlignmentFlag.AlignCenter)

        success_layout = QVBoxLayout()

        button_end_interaction = QPushButton(Translations.get_translation("end_interaction", True))
        button_end_interaction.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_end_interaction.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_end_interaction.clicked.connect(lambda: self.end_interaction())

        button_register_user = QPushButton(Translations.get_translation("register_user", True))
        button_register_user.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_register_user.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_register_user.clicked.connect(lambda: self.switch_frames(index_register_frame))

        button_manage_users = QPushButton(Translations.get_translation("manage_users", True))
        button_manage_users.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_manage_users.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_manage_users.clicked.connect(lambda: self.switch_frames(index_manage_users))

        max_width = max(round(button_end_interaction.width() / 2), round(button_register_user.width() / 2), round(button_manage_users.width() / 2))
        button_end_interaction.setMinimumWidth(max_width)
        button_register_user.setMinimumWidth(max_width)
        button_manage_users.setMinimumWidth(max_width)

        success_layout.addWidget(button_end_interaction)
        success_layout.addWidget(button_register_user)
        success_layout.addWidget(button_manage_users)

        # If there will be requirement to access users management only by admin then just update this condition
        # change const.IS_ADMIN to is_admin_logged
        if const.IS_ADMIN and conn.quick_check_internet_connection():
            button_manage_users.setHidden(False)
        else:
            button_manage_users.setHidden(True)

        self.grid_layout.addLayout(success_layout, 2, 1, Qt.AlignmentFlag.AlignCenter)

    def end_interaction(self):
        clear_global_variables()
        self.switch_frames(index_intro_frame)


class RegisterFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        first_phase_layout = QVBoxLayout()

        label_first_phase = QLabel(Translations.get_translation("registration_first_phase"))
        label_first_phase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_medium))
        label_first_phase.setStyleSheet(f"padding: {lbl_padding_20}px; color: #58a6d4;")
        label_first_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(False)
        progress_bar.setValue(round((1 / (2 + const.NUMBER_OF_VOICEPRINTS)) * 100))
        progress_bar.setFixedSize(label_first_phase.width(), (2 * btn_padding_t_b_30))
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        first_phase_layout.addWidget(label_first_phase)
        first_phase_layout.addWidget(progress_bar)
        self.grid_layout.addLayout(first_phase_layout, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_register_user = QLabel(
            "\n" + Translations.get_translation("new_register_come_closer_1") + "\n\n" + Translations.get_translation(
                "register_start_recording"))
        label_register_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_register_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_register_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_register_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_registrate = QPushButton(Translations.get_translation("registrate", True))
        button_registrate.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_registrate.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_registrate.clicked.connect(lambda: self.switch_frames(index_reg_first_phase_frame))
        self.grid_layout.addWidget(button_registrate, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_auth_success_frame))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)


class RegFirstPhaseCompleted(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global new_user_nickname, voiceprints_counter, recordings_counter

        number_of_voiceprints = const.NUMBER_OF_VOICEPRINTS

        if not conn.quick_check_internet_connection():
            number_of_voiceprints = number_of_voiceprints + 2

        if voiceprints_counter == 0:
            msg_info = f"New user nickname {new_user_nickname} registrated successfully."
            log.log_info(msg_info)

            # VOICE RECOGNITION
            if not os.path.isdir(const.SPEAKER_RECORDINGS_DIR):
                os.makedirs(const.SPEAKER_RECORDINGS_DIR, exist_ok=True)

            new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"

            if not os.path.isdir(new_user_dir):
                os.makedirs(new_user_dir, exist_ok=True)

            if conn.quick_check_internet_connection():
                new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
                manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)
                recordings_counter += 1

        if voiceprints_counter < number_of_voiceprints:
            super().create_items()

            second_phase_layout = QVBoxLayout()

            label_second_phase = QLabel(Translations.get_translation("registration_second_phase"))
            label_second_phase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_medium))
            label_second_phase.setStyleSheet(f"padding: {lbl_padding_20}px; color: #58a6d4;")
            label_second_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)

            progress_bar = QProgressBar(self)
            progress_bar.setRange(0, 100)
            progress_bar.setTextVisible(False)
            progress_bar.setValue(round(((recordings_counter + 1) / (2 + number_of_voiceprints)) * 100))
            progress_bar.setFixedSize(label_second_phase.width(), (2 * btn_padding_t_b_30))
            progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

            second_phase_layout.addWidget(label_second_phase)
            second_phase_layout.addWidget(progress_bar)
            self.grid_layout.addLayout(second_phase_layout, 1, 1, Qt.AlignmentFlag.AlignCenter)

            label_register_user = QLabel("\n" + Translations.get_translation("register_come_closer_2") +
                                         "\n\n" + Translations.get_translation("register_start_recording") +
                                         "\n\n" + Translations.get_translation('recording_number') +
                                         str(voiceprints_counter + 1) + ".")
            label_register_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
            label_register_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
            label_register_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
            self.grid_layout.addWidget(label_register_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

            button_registrate = QPushButton(Translations.get_translation("registrate", True))
            button_registrate.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
            button_registrate.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
            button_registrate.clicked.connect(lambda: self.switch_frames(index_reg_second_phase_frame))
            self.grid_layout.addWidget(button_registrate, 4, 1, Qt.AlignmentFlag.AlignCenter)

            button_back = QPushButton(Translations.get_translation("back", True))
            button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
            button_back.setStyleSheet(
                f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
                f"margin: {btn_margin_20}px;}} "
                f"QPushButton:hover {{ background-color: #58a6d4; }}")
            button_back.clicked.connect(lambda: self.turn_back())
            self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)
        else:
            voiceprints_counter = 0
            self.switch_frames(index_reg_second_phase_completed_frame)

    def turn_back(self):
        global new_user_nickname, voiceprints_counter, recordings_counter
        new_user_nickname = ""
        voiceprints_counter = 0
        recordings_counter = 0
        self.switch_frames(index_register_frame)


class RegSecondPhaseCompleted(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        super().create_items()

        third_phase_layout = QVBoxLayout()

        label_third_phase = QLabel(Translations.get_translation("registration_third_phase"))
        label_third_phase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_medium))
        label_third_phase.setStyleSheet(f"padding: {lbl_padding_20}px; color: #58a6d4;")
        label_third_phase.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(False)
        progress_bar.setValue(100)
        progress_bar.setFixedSize(label_third_phase.width(), (2 * btn_padding_t_b_30))
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        third_phase_layout.addWidget(label_third_phase)
        third_phase_layout.addWidget(progress_bar)
        self.grid_layout.addLayout(third_phase_layout, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_register_user = QLabel("\n" + Translations.get_translation("register_come_closer_3") +
                                     "\n\n" + Translations.get_translation("register_start_recording"))
        label_register_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_register_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_register_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_register_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        button_registrate = QPushButton(Translations.get_translation("registrate", True))
        button_registrate.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_registrate.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        button_registrate.clicked.connect(lambda: self.switch_frames(index_reg_third_phase_frame))
        self.grid_layout.addWidget(button_registrate, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.turn_back())
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)

    def turn_back(self):
        global new_user_nickname, voiceprints_counter, recordings_counter
        new_user_nickname = ""
        voiceprints_counter = 0
        recordings_counter = 0
        self.switch_frames(index_reg_first_phase_completed_frame)


class RegFirstPhaseFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global index_to_return, index_to_repeat, voiceprints_phrases, registration_with_internet
        index_to_return = index_register_frame
        index_to_repeat = index_reg_first_phase_frame

        super().create_items()

        voiceprints_phrases = list(const.VOICEPRINT_PHRASES[Translations.get_language()])
        registration_with_internet = conn.quick_check_internet_connection()

        self.label_register_user = QLabel(Translations.get_translation("recording"))
        self.label_register_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_register_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.label_register_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(self.label_register_user, 2, 1, Qt.AlignmentFlag.AlignCenter)

        if not conn.quick_check_internet_connection():
            asyncio.create_task(self.quick_check_internet_conn())
            return

        self.label_short_info = QLabel(Translations.get_translation("short_info_1"))
        self.label_short_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_short_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.label_short_info.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #f47e21; "
            f"border-radius: {border_radius_15};")
        self.label_short_info.setHidden(False)
        self.grid_layout.addWidget(self.label_short_info, 1, 1, Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.verify_speaker_name())

    async def quick_check_internet_conn(self):
        timeout = 10
        start_time = time.time()

        while not conn.quick_check_internet_connection():
            self.label_register_user.setText(Translations.get_translation("waiting_for_connection"))
            if time.time() - start_time >= timeout:
                break
            await asyncio.sleep(0.5)

        if conn.quick_check_internet_connection():
            self.clear_items()
            self.create_items()
        else:
            self.switch_frames(index_reg_not_internet_conn_frame)

    async def verify_speaker_name(self):
        global new_user_nickname

        await asyncio.sleep(0.5)

        if recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME):
            new_user_nickname = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                              Translations.get_language().lower())
            new_user_nickname = new_user_nickname.lower()

            msg_info = f"Recognized new user nickname: {new_user_nickname}"
            log.log_info(msg_info)

            self.label_register_user.setText(Translations.get_translation("recording_ended"))

            await asyncio.sleep(2)

            self.label_register_user.setText(Translations.get_translation("new_confirmation_nickname") + "\n\n" +
                                             new_user_nickname.upper())
            self.label_register_user.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.label_short_info.setHidden(True)

            button_repeat = QPushButton(Translations.get_translation("repeat", True))
            button_repeat.setFont(QFont(const.FONT_RHD_BOLD, font_small_medium))
            button_repeat.setStyleSheet(
                f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_60}px; "
                f"margin: {btn_margin_20}px;}} "
                f"QPushButton:hover {{ background-color: #58a6d4; }}")
            button_repeat.clicked.connect(lambda: self.repeat_registration())
            self.grid_layout.addWidget(button_repeat, 4, 0, Qt.AlignmentFlag.AlignLeft)

            button_confirm = QPushButton(Translations.get_translation("confirm", True))
            button_confirm.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
            button_confirm.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
            button_confirm.clicked.connect(lambda: self.switch_frames(index_reg_first_phase_completed_frame))
            self.grid_layout.addWidget(button_confirm, 4, 2, Qt.AlignmentFlag.AlignRight)

            if new_user_nickname in users:
                button_confirm.setEnabled(False)
                button_confirm.setStyleSheet(f"QPushButton:disabled {{padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;"
                                             f"background-color: #58a6d4; border: {border_width_5}px solid #f47e21;}}")
                self.label_register_user.setText(new_user_nickname.upper() + "\n\n" +
                                                 Translations.get_translation('new_nickname_exists_1') +
                                                 "\n\n" + Translations.get_translation('new_nickname_exists_2'))
                self.label_register_user.setStyleSheet(f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_60}px; "
                                                       f"background-color: #58a6d4; border-radius: {border_radius_15};"
                                                       f"border: {border_width_5}px solid #f47e21;")
                self.label_register_user.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            msg_error = f"Recording was not created. Please check your microphone settings."
            log.log_warning(msg_error)
            self.repeat_registration()

    def repeat_registration(self):
        self.clear_items()
        self.create_items()


class RegSecondPhaseFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global index_to_return, index_to_repeat, voiceprints_phrases
        index_to_return = index_reg_first_phase_completed_frame
        index_to_repeat = index_reg_second_phase_frame

        super().create_items()

        label_short_info = QLabel(Translations.get_translation("short_info_2"))
        label_short_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_short_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_short_info.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #f47e21; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_short_info, 1, 1, Qt.AlignmentFlag.AlignCenter)

        labels_layout = QVBoxLayout()

        self.label_register_user = QLabel(Translations.get_translation("recording"))
        self.label_register_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_register_user.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_register_user.setStyleSheet(f"padding: {lbl_padding_20}px;")

        random_phrase = s_recognizer.generate_random_word(voiceprints_phrases)
        voiceprints_phrases.remove(random_phrase)

        self.label_random_phrase = QLabel("\n" + random_phrase + "\n")
        self.label_random_phrase.setFont(QFont(const.FONT_RALEWAY_BOLD, font_small))
        self.label_random_phrase.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_random_phrase.setStyleSheet(
            f"padding: {lbl_padding_20}px; word-spacing: {lbl_padding_10}px; font-style: italic;")

        labels_layout.addWidget(self.label_random_phrase)
        labels_layout.addWidget(self.label_register_user)
        self.grid_layout.addLayout(labels_layout, 2, 1, Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.record_spoken_phrase())

    async def record_spoken_phrase(self):
        global new_user_nickname, voiceprints_counter, recordings_counter

        voiceprints_counter += 1

        await asyncio.sleep(0.5)

        if recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME, 6):
            msg_info = f"Voiceprint recording no.{str(voiceprints_counter)} recorded successfully."
            log.log_info(msg_info)

            # VOICE RECOGNITION
            new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"
            new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
            manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)
            recordings_counter += 1

            self.label_register_user.setText(Translations.get_translation("recording_ended"))
            self.label_random_phrase.setHidden(True)

            await asyncio.sleep(2)

            msg_info = f"Voiceprint {voiceprints_counter} recorded successfully."
            log.log_info(msg_info)

            self.switch_frames(index_reg_first_phase_completed_frame)
        else:
            msg_error = f"Recording was not created. Please check your microphone settings."
            log.log_warning(msg_error)
            self.switch_frames(index_reg_first_phase_completed_frame)


class RegThirdPhaseFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    def create_items(self):
        global index_to_return, index_to_repeat, registration_with_internet
        index_to_return = index_reg_second_phase_completed_frame
        index_to_repeat = index_reg_third_phase_frame

        super().create_items()

        if registration_with_internet and not conn.quick_check_internet_connection():
            registration_with_internet = conn.check_internet_connection()

        self.label_register_unique_phrase = QLabel(Translations.get_translation("recording"))
        self.label_register_unique_phrase.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_register_unique_phrase.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.label_register_unique_phrase.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(self.label_register_unique_phrase, 2, 1, Qt.AlignmentFlag.AlignCenter)

        if not conn.quick_check_internet_connection():
            asyncio.create_task(self.quick_check_internet_conn())
            return

        self.label_short_info = QLabel(Translations.get_translation("short_info_3"))
        self.label_short_info.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        self.label_short_info.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.label_short_info.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #f47e21; "
            f"border-radius: {border_radius_15};")
        self.label_short_info.setHidden(False)
        self.grid_layout.addWidget(self.label_short_info, 1, 1, Qt.AlignmentFlag.AlignCenter)

        asyncio.create_task(self.verify_speaker_unique_phrase())

    async def quick_check_internet_conn(self):
        timeout = 10
        start_time = time.time()

        while not conn.quick_check_internet_connection():
            self.label_register_unique_phrase.setText(Translations.get_translation("waiting_for_connection"))
            if time.time() - start_time >= timeout:
                break
            await asyncio.sleep(0.5)

        if conn.quick_check_internet_connection():
            self.clear_items()
            self.create_items()
        else:
            self.switch_frames(index_reg_not_internet_conn_frame)

    async def verify_speaker_unique_phrase(self):
        global new_user_unique_phrase

        await asyncio.sleep(0.5)

        if recorder.record_and_save_audio(const.RECORDED_AUDIO_FILENAME):
            new_user_unique_phrase = s_recognizer.recognize_speech(const.RECORDED_AUDIO_FILENAME,
                                                                   Translations.get_language().lower())
            new_user_unique_phrase = new_user_unique_phrase.lower()

            msg_info = f"Recognized new user unique phrase: {string_hasher.encode_string(new_user_unique_phrase)}"
            log.log_info(msg_info)

            self.label_register_unique_phrase.setText(Translations.get_translation("recording_ended"))

            await asyncio.sleep(2)

            self.label_register_unique_phrase.setText(Translations.get_translation("new_confirmation_phrase") +
                                                      "\n\n" + new_user_unique_phrase.upper())
            self.label_register_unique_phrase.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.label_short_info.setHidden(True)

            button_repeat = QPushButton(Translations.get_translation("repeat", True))
            button_repeat.setFont(QFont(const.FONT_RHD_BOLD, font_small_medium))
            button_repeat.setStyleSheet(
                f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_60}px; "
                f"margin: {btn_margin_20}px;}} "
                f"QPushButton:hover {{ background-color: #58a6d4; }}")
            button_repeat.clicked.connect(lambda: self.repeat_registration())
            self.grid_layout.addWidget(button_repeat, 4, 0, Qt.AlignmentFlag.AlignLeft)

            button_confirm = QPushButton(Translations.get_translation("confirm", True))
            button_confirm.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
            button_confirm.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
            button_confirm.clicked.connect(lambda: self.switch_frames(index_reg_success_frame))
            self.grid_layout.addWidget(button_confirm, 4, 2, Qt.AlignmentFlag.AlignRight)
        else:
            msg_error = f"Recording was not created. Please check your microphone settings."
            log.log_warning(msg_error)
            self.repeat_registration()

    def repeat_registration(self):
        self.clear_items()
        self.create_items()


class RegNotInternetConnFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    @asyncSlot()
    async def create_items(self):
        global index_to_return

        super().create_items()

        label_not_connection = QLabel(Translations.get_translation("internet", True))
        label_not_connection.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_not_connection.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_not_connection.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_not_connection, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_limited_mode = QLabel(Translations.get_translation("limited_mode") +
                                    "\n\n" + Translations.get_translation("nickname_to_continue"))
        label_limited_mode.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_limited_mode.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_limited_mode.setStyleSheet(f"padding: {lbl_padding_20}px;")
        label_limited_mode.setHidden(True)
        self.grid_layout.addWidget(label_limited_mode, 2, 1, Qt.AlignmentFlag.AlignCenter)

        label_register_user = QLabel(Translations.get_translation('new_nickname_exists_not_internet') +
                                     Translations.get_translation('nickname_exists_2')
                                     + "\n\n" + Translations.get_translation('nickname_exists_3'))
        label_register_user.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small))
        label_register_user.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_register_user.setStyleSheet(f"padding: {lbl_padding_20}px;")
        label_register_user.setHidden(True)
        self.grid_layout.addWidget(label_register_user, 3, 1, Qt.AlignmentFlag.AlignCenter)

        button_back = QPushButton(Translations.get_translation("back", True))
        button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_back.setStyleSheet(
            f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_60}px; "
            f"margin: {btn_margin_20}px;}} "
            f"QPushButton:hover {{ background-color: #58a6d4; }}")
        button_back.clicked.connect(lambda: self.switch_frames(index_to_return))
        self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignLeft)

        self.entry_register = QLineEdit()
        self.entry_register.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        self.entry_register.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_register.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
        self.grid_layout.addWidget(self.entry_register, 4, 1, Qt.AlignmentFlag.AlignCenter)

        button_confirm = QPushButton(Translations.get_translation("confirm", True))
        button_confirm.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
        button_confirm.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_30}px;")
        button_confirm.clicked.connect(lambda: self.confirm_register(self.entry_register.text()))
        self.grid_layout.addWidget(button_confirm, 4, 2, Qt.AlignmentFlag.AlignRight)

        if index_to_return == index_register_frame:
            label_limited_mode.setHidden(False)

            if new_user_nickname in users:
                label_register_user.setHidden(False)
                label_register_user.setStyleSheet(f"padding: {lbl_padding_20}px; border-radius: {border_radius_15}px; "
                                                  f"border: {border_width_5}px solid #f47e21;")
                await asyncio.sleep(5)
                label_register_user.setHidden(True)
            else:
                label_register_user.setHidden(True)

        elif index_to_return == index_reg_second_phase_completed_frame:
            label_limited_mode.setText(Translations.get_translation("limited_mode") +
                                        "\n\n" + Translations.get_translation("phrase_to_continue"))
            label_limited_mode.setHidden(False)

            label_register_user.setHidden(True)

    @asyncSlot()
    async def confirm_register(self, value):
        global index_to_return, new_user_nickname, new_user_unique_phrase

        if index_to_return == index_register_frame:
            new_user_nickname = value.lower()
            if new_user_nickname in users:
                self.clear_items()
                await self.create_items()
            else:
                self.switch_frames(index_reg_first_phase_completed_frame)
        elif index_to_return == index_reg_second_phase_completed_frame:
            new_user_unique_phrase = value.lower()
            self.switch_frames(index_reg_success_frame)


class RegSuccessFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    @asyncSlot()
    async def create_items(self):
        global new_user_nickname, new_user_unique_phrase, users, recordings_counter, registration_with_internet

        super().create_items()

        msg_info = f"New unique phrase {string_hasher.encode_string(new_user_unique_phrase)} registered successfully."
        log.log_info(msg_info)

        new_user_dir = const.SPEAKER_RECORDINGS_DIR + new_user_nickname + "/"

        if conn.quick_check_internet_connection():
            # VOICE RECOGNITION
            new_user_file = new_user_nickname + "_" + str(recordings_counter) + ".wav"
            manager.move_and_rename_audio(const.RECORDED_AUDIO_FILENAME, new_user_file, new_user_dir)

        recordings_counter = 0

        label_registration_success = QLabel(Translations.get_translation("registration_success", True))
        label_registration_success.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_registration_success.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_registration_success.setStyleSheet(
            f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
            f"border-radius: {border_radius_15};")
        self.grid_layout.addWidget(label_registration_success, 1, 1, Qt.AlignmentFlag.AlignCenter)

        label_processing = QLabel(Translations.get_translation("processing_voiceprints"))
        label_processing.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
        label_processing.setAlignment(Qt.AlignmentFlag.AlignJustify)
        label_processing.setStyleSheet(f"padding: {lbl_padding_20}px;")
        self.grid_layout.addWidget(label_processing, 2, 1, Qt.AlignmentFlag.AlignCenter)

        await asyncio.sleep(2)

        user_values = string_hasher.encode_string(new_user_unique_phrase) + (registration_with_internet,)

        if json.add_user_to_json_file(users, new_user_nickname,
                                      user_values,
                                      const.USERS_FILENAME):

            if not os.path.isdir(const.SPEAKER_VOICEPRINTS_DIR):
                os.makedirs(const.SPEAKER_VOICEPRINTS_DIR, exist_ok=True)

            output_dir = const.SPEAKER_VOICEPRINTS_DIR + new_user_nickname + "/"

            if not os.path.isdir(output_dir):
                os.makedirs(output_dir, exist_ok=True)

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

        self.end_interaction()

    def end_interaction(self):
        clear_global_variables()
        self.switch_frames(index_intro_frame)


class ManageUsersFrame(Frame):
    def __init__(self, switch_frames):
        super().__init__()

        self.switch_frames = switch_frames

    @asyncSlot()
    async def create_items(self):
        global is_admin_logged

        super().create_items()

        if conn.quick_check_internet_connection():
            users_to_show = users.copy()

            if not is_admin_logged:
                del users_to_show[currently_logged_user]

            combobox_users = QComboBox()
            combobox_users.addItems(list(users_to_show.keys()))
            combobox_users.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
            combobox_users.setEditable(False)
            combobox_users.setMinimumWidth(500)
            combobox_users.setMaxVisibleItems(3)
            combobox_users.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.grid_layout.addWidget(combobox_users, 1, 1, Qt.AlignmentFlag.AlignCenter)

            button_delete_user = QPushButton(Translations.get_translation("delete", True))
            button_delete_user.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
            button_delete_user.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; margin: {btn_margin_20}px;")
            button_delete_user.clicked.connect(lambda: self.delete_user(combobox_users.currentText()))
            self.grid_layout.addWidget(button_delete_user, 4, 1, Qt.AlignmentFlag.AlignCenter)

            button_back = QPushButton(Translations.get_translation("back", True))
            button_back.setFont(QFont(const.FONT_RHD_BOLD, font_medium))
            button_back.setStyleSheet(
                f"QPushButton {{background-color: #a2d5ec; padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; "
                f"margin: {btn_margin_20}px;}} "
                f"QPushButton:hover {{ background-color: #58a6d4; }}")
            button_back.clicked.connect(lambda: self.switch_frames(index_auth_success_frame))
            self.grid_layout.addWidget(button_back, 4, 0, Qt.AlignmentFlag.AlignCenter)
        else:
            label_not_connection = QLabel(Translations.get_translation("internet", True))
            label_not_connection.setFont(QFont(const.FONT_RALEWAY_MEDIUM, font_small_medium))
            label_not_connection.setAlignment(Qt.AlignmentFlag.AlignJustify)
            label_not_connection.setStyleSheet(
                f"padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px; background-color: #58a6d4; "
                f"border-radius: {border_radius_15};")
            self.grid_layout.addWidget(label_not_connection, 1, 1, Qt.AlignmentFlag.AlignCenter)

            await asyncio.sleep(2)

            self.switch_frames(index_auth_success_frame)

    def delete_user(self, value):
        global user_to_delete, users
        user_to_delete = value

        if conn.quick_check_internet_connection():
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
        self.switch_frames(index_manage_users)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        global simple_mode

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
        self.first_phase_success_frame = FirstPhaseSuccess(self.switch_frame)
        self.second_phase_success_frame = SecondPhaseSuccess(self.switch_frame)
        self.auth_first_phase_frame = AuthFirstPhaseFrame(self.switch_frame)
        self.auth_second_phase_frame = AuthSecondPhaseFrame(self.switch_frame)
        self.auth_third_phase_frame = AuthThirdPhaseFrame(self.switch_frame)
        self.not_internet_conn_frame = NotInternetConnFrame(self.switch_frame)
        self.auth_unsuccess_frame = AuthUnsuccessFrame(self.switch_frame)
        self.auth_success_frame = AuthSuccessFrame(self.switch_frame)
        self.register_frame = RegisterFrame(self.switch_frame)
        self.reg_first_phase_completed_frame = RegFirstPhaseCompleted(self.switch_frame)
        self.reg_second_phase_completed_frame = RegSecondPhaseCompleted(self.switch_frame)
        self.reg_first_phase_frame = RegFirstPhaseFrame(self.switch_frame)
        self.reg_second_phase_frame = RegSecondPhaseFrame(self.switch_frame)
        self.reg_third_phase_frame = RegThirdPhaseFrame(self.switch_frame)
        self.reg_not_internet_conn_frame = RegNotInternetConnFrame(self.switch_frame)
        self.reg_success_frame = RegSuccessFrame(self.switch_frame)
        self.manage_users_frame = ManageUsersFrame(self.switch_frame)

        self.stacked_widget.addWidget(self.intro_frame)
        self.stacked_widget.addWidget(self.open_door_frame)
        self.stacked_widget.addWidget(self.admin_frame)
        self.stacked_widget.addWidget(self.about_frame)
        self.stacked_widget.addWidget(self.sign_in_frame)
        self.stacked_widget.addWidget(self.sign_up_frame)
        self.stacked_widget.addWidget(self.first_phase_success_frame)
        self.stacked_widget.addWidget(self.second_phase_success_frame)
        self.stacked_widget.addWidget(self.auth_first_phase_frame)
        self.stacked_widget.addWidget(self.auth_second_phase_frame)
        self.stacked_widget.addWidget(self.auth_third_phase_frame)
        self.stacked_widget.addWidget(self.not_internet_conn_frame)
        self.stacked_widget.addWidget(self.auth_unsuccess_frame)
        self.stacked_widget.addWidget(self.auth_success_frame)
        self.stacked_widget.addWidget(self.register_frame)
        self.stacked_widget.addWidget(self.reg_first_phase_completed_frame)
        self.stacked_widget.addWidget(self.reg_second_phase_completed_frame)
        self.stacked_widget.addWidget(self.reg_first_phase_frame)
        self.stacked_widget.addWidget(self.reg_second_phase_frame)
        self.stacked_widget.addWidget(self.reg_third_phase_frame)
        self.stacked_widget.addWidget(self.reg_not_internet_conn_frame)
        self.stacked_widget.addWidget(self.reg_success_frame)
        self.stacked_widget.addWidget(self.manage_users_frame)

        self.intro_frame.create_items()
        self.create_menu()
        self.apply_styles()

    def create_menu(self):
        self.menu_bar = self.menuBar()
        self.menu_bar.setFont(QFont(const.FONT_RHD_MEDIUM, font_small))

        intro_action = QAction(Translations.get_translation("intro"), self)
        intro_action.triggered.connect(lambda: self.change_frame(index_intro_frame))

        about_action = QAction(Translations.get_translation("about_project"), self)
        about_action.triggered.connect(lambda: self.change_frame(index_about_frame))

        admin_action = QAction(Translations.get_translation("admin"), self)
        admin_action.triggered.connect(lambda: self.change_frame(index_admin_frame))

        exit_action = QAction(Translations.get_translation("exit"), self)
        exit_action.triggered.connect(lambda: sys.exit())

        self.menu_bar.addActions([intro_action, about_action, admin_action, exit_action])

    def change_frame(self, index):
        clear_global_variables()
        self.switch_frame(index)

    def update_menubar_items_translations(self):
        self.setWindowTitle(Translations.get_translation("system_authentication"))
        self.menu_bar.actions()[0].setText(Translations.get_translation("intro"))
        self.menu_bar.actions()[1].setText(Translations.get_translation("about_project"))
        self.menu_bar.actions()[2].setText(Translations.get_translation("admin"))
        self.menu_bar.actions()[3].setText(Translations.get_translation("exit"))

    def switch_frame(self, index):
        self.stacked_widget.currentWidget().clear_items()
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
            QComboBox {{
                background-color: #58a6d4;
                color: #000000;
                border-radius: {border_radius_15}px;
                border: {border_width_5}px solid #000000;
                padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px;
                margin: {btn_margin_0}px {btn_margin_0}px {btn_margin_20}px {btn_margin_0}px;
                combobox-popup: 0;
            }}
            QComboBox::drop-down {{
                width: {btn_padding_l_r_80}px;
                border-left: {border_width_5}px solid #000000;
                border-top-right-radius: {border_radius_10}px;
                border-bottom-right-radius: {border_radius_10}px;
            }}
            QComboBox::drop-down:hover {{
                background-color: #f47e21;
            }}
            QComboBox::down-arrow {{
                image: url(drop_down_arrow.png);
                width: {btn_padding_l_r_80}px;
                height: {btn_padding_l_r_60}px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: none;
                border-radius: {border_radius_15}px;
                width: {btn_padding_l_r_80}px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #f47e21;
                border-radius: {border_radius_15}px;
                border: {border_width_5}px solid #000000;
                min-height: {btn_padding_t_b_30}px;
            }}
            QScrollBar::add-line:vertical {{
                background: none;
                height: {btn_padding_t_b_30}px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line:vertical {{
                background: none;
                height: {btn_padding_t_b_30}px;
                subcontrol-position: top left;
                subcontrol-origin: margin;
                position: absolute;
            }}    
            QScrollBar:up-arrow:vertical {{
                width: {btn_padding_t_b_30}px;
                height: {btn_padding_t_b_30}px;
                background: none;
                image: url('drop_up_arrow.png');
            }}
            QScrollBar::down-arrow:vertical {{
                width: {btn_padding_t_b_30}px;
                height: {btn_padding_t_b_30}px;
                background: none;
                image: url('drop_down_arrow.png');
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
                background-color: #58a6d4;
            }}
            QListView {{
                outline: none;
                background-color: #58a6d4;
                color: #000000;
                border-radius: {border_radius_15}px;
            }}
            QListView::item {{  
                background-color: #58a6d4;
                color: #000000;
                border-radius: {border_radius_15}px;
                padding: {btn_padding_t_b_30}px {btn_padding_l_r_80}px;
            }}
            QListView::item:hover {{
                background-color: #f47e21;
                border: {border_width_5}px solid #000000;
            }}
        """)

    def initialize_screen_resolution(self):
        global font_large, font_medium, font_small_medium, font_small
        global rescale_factor
        global btn_padding_t_b_20, btn_padding_t_b_30, btn_padding_t_b_60
        global btn_padding_l_r_30, btn_padding_l_r_40, btn_padding_l_r_60, btn_padding_l_r_80
        global btn_margin_0, btn_margin_20
        global lbl_padding_10, lbl_padding_20
        global img_margin_30, img_margin_40
        global border_width_5, border_radius_10, border_radius_15

        window_width = QApplication.primaryScreen().size().width()
        window_height = QApplication.primaryScreen().size().height()

        font_sizes = initialize_font_sizes(window_width, window_height)
        font_large, font_medium, font_small_medium, font_small = font_sizes[0], font_sizes[1], font_sizes[2], font_sizes[3]

        rescale_factor = initialize_image_sizes(window_width, window_height)

        btn_padding_t_b_20 = initialize_paddings_margins(const.BTN_PADDING_T_B_20, window_width, window_height)
        btn_padding_t_b_30 = initialize_paddings_margins(const.BTN_PADDING_T_B_30, window_width, window_height)
        btn_padding_t_b_60 = initialize_paddings_margins(const.BTN_PADDING_T_B_60, window_width, window_height)
        btn_padding_l_r_30 = initialize_paddings_margins(const.BTN_PADDING_L_R_30, window_width, window_height)
        btn_padding_l_r_40 = initialize_paddings_margins(const.BTN_PADDING_L_R_40, window_width, window_height)
        btn_padding_l_r_60 = initialize_paddings_margins(const.BTN_PADDING_L_R_60, window_width, window_height)
        btn_padding_l_r_80 = initialize_paddings_margins(const.BTN_PADDING_L_R_80, window_width, window_height)
        btn_margin_0 = initialize_paddings_margins(const.BTN_MARGIN_0, window_width, window_height)
        btn_margin_20 = initialize_paddings_margins(const.BTN_MARGIN_20, window_width, window_height)
        lbl_padding_10 = initialize_paddings_margins(const.LBL_PADDING_10, window_width, window_height)
        lbl_padding_20 = initialize_paddings_margins(const.LBL_PADDING_20, window_width, window_height)
        img_margin_30 = initialize_paddings_margins(const.IMG_MARGIN_30, window_width, window_height)
        img_margin_40 = initialize_paddings_margins(const.IMG_MARGIN_40, window_width, window_height)
        border_width_5 = initialize_paddings_margins(const.BORDER_WIDTH_5, window_width, window_height)
        border_radius_10 = initialize_paddings_margins(const.BORDER_RADIUS_10, window_width, window_height)
        border_radius_15 = initialize_paddings_margins(const.BORDER_RADIUS_15, window_width, window_height)


simple_mode = False
skip_auth_info = False
is_admin_logged = False
registration_with_internet = True
currently_logged_user = ""
user_to_delete = ""
new_user_nickname = ""
new_user_unique_phrase = ""
index_to_return = -1
index_to_repeat = -1
voiceprints_counter = 0
recordings_counter = 0
remaining_attempts = 3
partial_authentication = 0.0

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


def main():
    global simple_mode

    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--simple", required=False,
                    help="put True if launch simple mode")
    args = vars(ap.parse_args())

    if len(sys.argv) > 1:
        if args["simple"] == "True":
            simple_mode = bool(args["simple"])

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
